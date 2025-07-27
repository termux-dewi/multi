FROM python:3.11-alpine

# Install dependencies (OpenSSH, bash, etc.)
RUN apk add --no-cache openssh bash

# Setup SSH
RUN echo 'root:1' | chpasswd && \
    sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    mkdir -p /var/run/sshd

# Expose ports
EXPOSE 9000 8022 5000 5900 5555 22

# Create working directory
WORKDIR /app

# Copy your Python multiplexer script
COPY multiplexer.py .

# Create entrypoint script
RUN echo '#!/bin/sh\n\
/usr/sbin/sshd && python3 /app/multiplexer.py' > /start.sh && \
    chmod +x /start.sh

# Run both SSH server and Python multiplexer
CMD ["/bin/sh", "/start.sh"]
