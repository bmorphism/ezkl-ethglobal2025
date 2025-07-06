#!/usr/bin/env python3
"""
Real-time Proof Streaming Infrastructure - PRODUCTION IMPLEMENTATION
WebSocket-based streaming for live agentic coordination
"""

import asyncio
import json
import logging
import websockets
import time
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from collections import defaultdict
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    PROOF_SUBMITTED = "proof_submitted"
    VERIFICATION_COMPLETE = "verification_complete" 
    CHAIN_STEP_ADDED = "chain_step_added"
    STREAM_CREATED = "stream_created"
    AGENT_REGISTERED = "agent_registered"
    TASK_DELEGATED = "task_delegated"
    OPERAD_COMPLETED = "operad_completed"

@dataclass
class StreamEvent:
    event_type: EventType
    stream_id: str
    timestamp: float
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None

@dataclass
class StreamFilter:
    architectures: List[str] = None
    agents: List[str] = None
    event_types: List[EventType] = None
    quality_threshold: float = None
    chain_id: str = None

class ProofStreamingServer:
    """Production-grade WebSocket streaming server for real-time proof coordination"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connected_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.client_subscriptions: Dict[str, List[StreamFilter]] = defaultdict(list)
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.server = None
        self.running = False
        
        # Metrics
        self.metrics = {
            "total_events": 0,
            "events_per_second": 0,
            "connected_clients": 0,
            "active_streams": 0,
            "average_latency": 0
        }
        
        # Performance tracking
        self._last_metrics_update = time.time()
        self._events_since_last_update = 0
        
    async def start_server(self):
        """Start the WebSocket streaming server"""
        logger.info(f"Starting Proof Streaming Server on ws://{self.host}:{self.port}")
        
        async def handle_client(websocket, path):
            await self._handle_client(websocket, path)
            
        self.server = await websockets.serve(handle_client, self.host, self.port)
        self.running = True
        
        # Start metrics updater
        asyncio.create_task(self._update_metrics_loop())
        
        logger.info(f"Proof Streaming Server running on ws://{self.host}:{self.port}")
        await self.server.wait_closed()
    
    async def stop_server(self):
        """Stop the streaming server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.running = False
            logger.info("Proof Streaming Server stopped")
    
    async def _handle_client(self, websocket, path):
        """Handle new WebSocket client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}:{time.time()}"
        
        try:
            self.connected_clients[client_id] = websocket
            self.metrics["connected_clients"] = len(self.connected_clients)
            logger.info(f"Client connected: {client_id}")
            
            # Send welcome message
            await self._send_to_client(client_id, {
                "type": "connection_established",
                "client_id": client_id,
                "server_info": {
                    "version": "1.0.0",
                    "features": ["proof_streaming", "real_time_coordination", "agent_discovery"],
                    "active_streams": len(self.active_streams)
                }
            })
            
            # Handle incoming messages
            async for message in websocket:
                await self._handle_client_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Cleanup
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
            self.metrics["connected_clients"] = len(self.connected_clients)
    
    async def _handle_client_message(self, client_id: str, message: str):
        """Handle messages from WebSocket clients"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "subscribe":
                await self._handle_subscription(client_id, data)
            elif msg_type == "unsubscribe":
                await self._handle_unsubscription(client_id, data)
            elif msg_type == "create_stream":
                await self._handle_create_stream(client_id, data)
            elif msg_type == "submit_proof":
                await self._handle_proof_submission(client_id, data)
            elif msg_type == "ping":
                await self._send_to_client(client_id, {"type": "pong", "timestamp": time.time()})
            else:
                await self._send_to_client(client_id, {
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })
                
        except json.JSONDecodeError:
            await self._send_to_client(client_id, {
                "type": "error", 
                "message": "Invalid JSON format"
            })
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self._send_to_client(client_id, {
                "type": "error",
                "message": str(e)
            })
    
    async def _handle_subscription(self, client_id: str, data: Dict[str, Any]):
        """Handle client subscription to proof streams"""
        try:
            filter_data = data.get("filter", {})
            stream_filter = StreamFilter(
                architectures=filter_data.get("architectures"),
                agents=filter_data.get("agents"),
                event_types=[EventType(et) for et in filter_data.get("event_types", [])],
                quality_threshold=filter_data.get("quality_threshold"),
                chain_id=filter_data.get("chain_id")
            )
            
            self.client_subscriptions[client_id].append(stream_filter)
            
            await self._send_to_client(client_id, {
                "type": "subscription_confirmed",
                "filter": asdict(stream_filter),
                "subscription_id": len(self.client_subscriptions[client_id]) - 1
            })
            
            logger.info(f"Client {client_id} subscribed with filter: {filter_data}")
            
        except Exception as e:
            await self._send_to_client(client_id, {
                "type": "subscription_error",
                "message": str(e)
            })
    
    async def _handle_unsubscription(self, client_id: str, data: Dict[str, Any]):
        """Handle client unsubscription"""
        subscription_id = data.get("subscription_id")
        
        if client_id in self.client_subscriptions:
            if subscription_id is not None and 0 <= subscription_id < len(self.client_subscriptions[client_id]):
                del self.client_subscriptions[client_id][subscription_id]
                await self._send_to_client(client_id, {
                    "type": "unsubscription_confirmed",
                    "subscription_id": subscription_id
                })
            else:
                # Clear all subscriptions
                self.client_subscriptions[client_id].clear()
                await self._send_to_client(client_id, {
                    "type": "all_subscriptions_cleared"
                })
    
    async def _handle_create_stream(self, client_id: str, data: Dict[str, Any]):
        """Handle stream creation request"""
        try:
            stream_spec = data.get("stream_spec", {})
            stream_id = hashlib.sha256(
                f"{client_id}_{stream_spec}_{time.time()}".encode()
            ).hexdigest()
            
            self.active_streams[stream_id] = {
                "id": stream_id,
                "creator": client_id,
                "spec": stream_spec,
                "created_at": time.time(),
                "event_count": 0,
                "subscribers": []
            }
            
            self.metrics["active_streams"] = len(self.active_streams)
            
            await self._send_to_client(client_id, {
                "type": "stream_created",
                "stream_id": stream_id,
                "spec": stream_spec
            })
            
            # Broadcast stream creation
            await self._emit_event(StreamEvent(
                event_type=EventType.STREAM_CREATED,
                stream_id=stream_id,
                timestamp=time.time(),
                data={"creator": client_id, "spec": stream_spec}
            ))
            
            logger.info(f"Stream created: {stream_id}")
            
        except Exception as e:
            await self._send_to_client(client_id, {
                "type": "stream_creation_error",
                "message": str(e)
            })
    
    async def _handle_proof_submission(self, client_id: str, data: Dict[str, Any]):
        """Handle proof submission to stream"""
        try:
            stream_id = data.get("stream_id")
            proof_data = data.get("proof_data")
            public_inputs = data.get("public_inputs")
            
            if stream_id not in self.active_streams:
                raise ValueError(f"Stream {stream_id} not found")
            
            # Emit proof submission event
            await self._emit_event(StreamEvent(
                event_type=EventType.PROOF_SUBMITTED,
                stream_id=stream_id,
                timestamp=time.time(),
                data={
                    "submitter": client_id,
                    "proof_hash": hashlib.sha256(str(proof_data).encode()).hexdigest()[:16],
                    "input_hash": hashlib.sha256(str(public_inputs).encode()).hexdigest()[:16],
                    "architecture": data.get("architecture", "unknown")
                }
            ))
            
            # Update stream metrics
            self.active_streams[stream_id]["event_count"] += 1
            
            await self._send_to_client(client_id, {
                "type": "proof_submitted",
                "stream_id": stream_id,
                "status": "accepted"
            })
            
        except Exception as e:
            await self._send_to_client(client_id, {
                "type": "proof_submission_error",
                "message": str(e)
            })
    
    async def _emit_event(self, event: StreamEvent):
        """Emit event to all subscribed clients"""
        self.metrics["total_events"] += 1
        self._events_since_last_update += 1
        
        event_data = {
            "type": "stream_event",
            "event": asdict(event),
            "timestamp": time.time()
        }
        
        # Send to subscribers
        for client_id, filters in self.client_subscriptions.items():
            if self._event_matches_filters(event, filters):
                await self._send_to_client(client_id, event_data)
        
        # Call registered event handlers
        for handler in self.event_handlers[event.event_type]:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
    
    def _event_matches_filters(self, event: StreamEvent, filters: List[StreamFilter]) -> bool:
        """Check if event matches client filters"""
        if not filters:
            return True
            
        for f in filters:
            # Check event type filter
            if f.event_types and event.event_type not in f.event_types:
                continue
                
            # Check architecture filter
            if f.architectures and event.data.get("architecture") not in f.architectures:
                continue
                
            # Check agent filter
            if f.agents:
                agent = event.data.get("agent") or event.data.get("submitter")
                if agent not in f.agents:
                    continue
            
            # Check quality threshold
            if f.quality_threshold:
                quality = event.data.get("quality_score", 0)
                if quality < f.quality_threshold:
                    continue
            
            # Check chain ID
            if f.chain_id and event.data.get("chain_id") != f.chain_id:
                continue
                
            # If we reach here, event matches this filter
            return True
            
        return False
    
    async def _send_to_client(self, client_id: str, data: Dict[str, Any]):
        """Send data to specific client"""
        if client_id not in self.connected_clients:
            return
            
        try:
            websocket = self.connected_clients[client_id]
            await websocket.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
            # Remove disconnected client
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
    
    async def _update_metrics_loop(self):
        """Update performance metrics periodically"""
        while self.running:
            await asyncio.sleep(5)  # Update every 5 seconds
            
            current_time = time.time()
            time_delta = current_time - self._last_metrics_update
            
            if time_delta > 0:
                self.metrics["events_per_second"] = self._events_since_last_update / time_delta
                
            self._last_metrics_update = current_time
            self._events_since_last_update = 0
            
            # Log metrics
            logger.info(f"Metrics: {self.metrics}")
    
    def add_event_handler(self, event_type: EventType, handler: Callable):
        """Add event handler for specific event type"""
        self.event_handlers[event_type].append(handler)
    
    async def broadcast_verification_complete(self, agent: str, receipt_hash: str, 
                                           architecture: str, gas_used: int):
        """Broadcast verification completion event"""
        await self._emit_event(StreamEvent(
            event_type=EventType.VERIFICATION_COMPLETE,
            stream_id="global",
            timestamp=time.time(),
            data={
                "agent": agent,
                "receipt_hash": receipt_hash,
                "architecture": architecture,
                "gas_used": gas_used,
                "verified": True
            }
        ))
    
    async def broadcast_chain_step_added(self, chain_id: str, step_index: int, 
                                       agent: str, architecture: str):
        """Broadcast chain step addition event"""
        await self._emit_event(StreamEvent(
            event_type=EventType.CHAIN_STEP_ADDED,
            stream_id="global",
            timestamp=time.time(),
            data={
                "chain_id": chain_id,
                "step_index": step_index,
                "agent": agent,
                "architecture": architecture
            }
        ))
    
    async def broadcast_agent_registered(self, agent: str, architectures: List[str]):
        """Broadcast agent registration event"""
        await self._emit_event(StreamEvent(
            event_type=EventType.AGENT_REGISTERED,
            stream_id="global",
            timestamp=time.time(),
            data={
                "agent": agent,
                "architectures": architectures,
                "reputation_score": 100  # Initial score
            }
        ))

class ProofStreamingClient:
    """Client for connecting to proof streaming server"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.websocket = None
        self.connected = False
        self.subscriptions = []
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
    
    async def connect(self):
        """Connect to streaming server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            logger.info(f"Connected to streaming server: {self.server_url}")
            
            # Start message handler
            asyncio.create_task(self._handle_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.server_url}: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from streaming server")
    
    async def subscribe(self, filters: Dict[str, Any] = None, event_types: List[str] = None):
        """Subscribe to proof stream events"""
        subscription = {
            "type": "subscribe",
            "filter": filters or {},
        }
        
        if event_types:
            subscription["filter"]["event_types"] = event_types
            
        await self._send_message(subscription)
    
    async def submit_proof(self, stream_id: str, proof_data: Dict[str, Any], 
                         public_inputs: List[Any], architecture: str = "RWKV"):
        """Submit proof to stream"""
        message = {
            "type": "submit_proof",
            "stream_id": stream_id,
            "proof_data": proof_data,
            "public_inputs": public_inputs,
            "architecture": architecture
        }
        
        await self._send_message(message)
    
    async def create_stream(self, stream_spec: Dict[str, Any]):
        """Create new proof stream"""
        message = {
            "type": "create_stream",
            "stream_spec": stream_spec
        }
        
        await self._send_message(message)
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send message to server"""
        if not self.connected or not self.websocket:
            raise ConnectionError("Not connected to server")
            
        await self.websocket.send(json.dumps(message))
    
    async def _handle_messages(self):
        """Handle incoming messages from server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                msg_type = data.get("type")
                
                # Call registered handlers
                for handler in self.event_handlers.get(msg_type, []):
                    try:
                        await handler(data)
                    except Exception as e:
                        logger.error(f"Error in event handler: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
            logger.info("Connection to server closed")
        except Exception as e:
            logger.error(f"Error handling messages: {e}")
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add handler for specific event type"""
        self.event_handlers[event_type].append(handler)

# Example usage
async def demo_streaming():
    """Demonstrate streaming functionality"""
    
    # Start server
    server = ProofStreamingServer()
    server_task = asyncio.create_task(server.start_server())
    
    # Give server time to start
    await asyncio.sleep(1)
    
    # Create client
    client = ProofStreamingClient("ws://localhost:8765")
    await client.connect()
    
    # Subscribe to events
    await client.subscribe(
        filters={"architectures": ["RWKV", "Mamba"]},
        event_types=["proof_submitted", "verification_complete"]
    )
    
    # Submit some proofs
    await client.submit_proof(
        stream_id="demo_stream",
        proof_data={"proof": "sample_proof_data"},
        public_inputs=[1, 2, 3, 4, 5],
        architecture="RWKV"
    )
    
    # Run for a while
    await asyncio.sleep(5)
    
    # Cleanup
    await client.disconnect()
    await server.stop_server()

if __name__ == "__main__":
    asyncio.run(demo_streaming())