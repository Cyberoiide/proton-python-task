# Dockerfile
FROM alpine:latest

RUN apk update && apk add --no-cache openssh bash

RUN adduser -D testuser && echo "testuser:password" | chpasswd

RUN mkdir -p /home/testuser/.ssh && \
    chown -R testuser:testuser /home/testuser/.ssh

RUN echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

RUN ssh-keygen -A

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]