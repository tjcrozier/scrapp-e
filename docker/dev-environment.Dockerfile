FROM ros:lyrical-ros-core

# update and install clang
USER root
RUN apt-get update
RUN apt-get install clang -y

# sets compiler for cmake to be clang (or should at least)
RUN CXX="clang"

# flags as dev environment for scrapp-e core
RUN SCRAPPE_DEBUG=TRUE
# RUN 'git clone '