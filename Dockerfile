# Stage 1: Base image with Node.js and Python
FROM node:18-slim AS base
RUN apt-get update && apt-get install -y python3 python3-pip curl

# Stage 2: Add EZKL binary
FROM base AS with-ezkl
ARG EZKL_VERSION=v10.4.2
ARG EZKL_ARCH=linux-gnu
RUN curl -L -o /usr/local/bin/ezkl https://github.com/zkonduit/ezkl/releases/download/${EZKL_VERSION}/build-artifacts.ezkl-${EZKL_ARCH}.tar.gz \
    && tar -xzf /usr/local/bin/ezkl -C /usr/local/bin/ \
    && rm /usr/local/bin/ezkl \
    && chmod +x /usr/local/bin/ezkl

# Stage 3: Application build
FROM with-ezkl AS build
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies using the lock file for reproducibility
COPY requirements.lock .
RUN npm install
RUN pip3 install --no-cache-dir -r requirements.lock

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "conduct.sh"]