FROM alpine:latest

# Install openssh dan bash
RUN apk add --no-cache openssh bash

# Buat folder runtime SSH
RUN mkdir -p /var/run/sshd

# Atur password root ke "1"
RUN echo "root:1" | chpasswd

# Ubah konfigurasi SSH agar root bisa login dengan password
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#Port 22/Port 22/' /etc/ssh/sshd_config

# Expose port SSH
EXPOSE 22

# Jalankan SSH saat container start
CMD ["/usr/sbin/sshd", "-D"]
