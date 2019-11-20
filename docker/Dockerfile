FROM alpine:latest
COPY tantivy-cli/bin/tantivy tantivy

# RUN apk update && apk add strace

# default tantivy-cli port
EXPOSE 3000
ENV RUST_BACKTRACE 1
ENTRYPOINT [           \ 
  # "strace", "-f",    \
  "/tantivy",          \
  "serve",             \
  "--index", "/scrapyroo-index", \
  "-p", "3000", \
                \
  # TODO ugh. not sure if it's tantivy-cli issue since e.g. python -m http.server works fine. investigate later \
  # https://nickjanetakis.com/blog/docker-tip-54-fixing-connection-reset-by-peer-or-similar-earrors \
  "--host", "0.0.0.0" \
]

# building: docker build -t scrapyroo
# running:  docker run -v /tmp/scrapyroo-index:/scrapyroo-index -p 3000:3000 scrapyroo