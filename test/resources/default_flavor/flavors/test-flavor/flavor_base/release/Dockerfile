FROM ubuntu:24.04


COPY --from={{flavor_customization}} /usr /usr
RUN true # workaround for https://github.com/moby/moby/issues/37965

COPY --from={{flavor_customization}} /lib /lib
RUN true # workaround for https://github.com/moby/moby/issues/37965

COPY --from={{flavor_customization}} /bin /bin
RUN true # workaround for https://github.com/moby/moby/issues/37965

COPY --from={{flavor_customization}} /opt /opt
RUN true # workaround for https://github.com/moby/moby/issues/37965

COPY --from={{flavor_customization}} /etc /etc
RUN true # workaround for https://github.com/moby/moby/issues/37965

COPY --from={{flavor_customization}} /build_info /build_info
RUN true # workaround for https://github.com/moby/moby/issues/37965


COPY language_definitions.json /build_info/language_definitions.json
RUN true # workaround for https://github.com/moby/moby/issues/37965

COPY /release_packages.yml /build_info/release_packages.yml
RUN true # workaround for https://github.com/moby/moby/issues/37965
