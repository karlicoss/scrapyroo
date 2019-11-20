# FROM alpine:latest
FROM ubuntu:bionic
COPY tantivy-cli/bin/tantivy tantivy

EXPOSE 3000
ENV RUST_BACKTRACE 1
ENTRYPOINT ["/tantivy", "serve", "--index", "/scrapyroo-index", "--host", "127.0.0.1"]
