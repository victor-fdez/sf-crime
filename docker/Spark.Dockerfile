FROM debian:stretch
MAINTAINER Victor Fernandez

RUN apt-get update \
 && apt-get install -y locales \
 && dpkg-reconfigure -f noninteractive locales \
 && locale-gen C.UTF-8 \
 && /usr/sbin/update-locale LANG=C.UTF-8 \
 && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
 && locale-gen \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Users with other locales should set this in their derivative image
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update \
 && apt-get install -y curl unzip \
    python3 python3-setuptools \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && easy_install3 pip py4j \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# http://blog.stuart.axelbrooke.com/python-3-on-spark-return-of-the-pythonhashseed
ENV PYTHONHASHSEED 0
ENV PYTHONIOENCODING UTF-8
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

# this installs packages mentioned in requirements-pip.txt
ADD requirements.txt .
RUN pip3 install --upgrade pip setuptools pypandoc && \
    pip3 install -r requirements.txt

# JAVA
RUN apt-get update \
 && apt-get install -y openjdk-8-jre \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# HADOOP
ENV HADOOP_VERSION 2.7 

# SPARK
ENV SPARK_VERSION 2.4.3
ENV SPARK_PACKAGE spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}
ENV SPARK_HOME /usr/spark-${SPARK_VERSION}
#ENV SPARK_DIST_CLASSPATH="$HADOOP_HOME/etc/hadoop/*:$HADOOP_HOME/share/hadoop/common/lib/*:$HADOOP_HOME/share/hadoop/common/*:$HADOOP_HOME/share/hadoop/hdfs/*:$HADOOP_HOME/share/hadoop/hdfs/lib/*:$HADOOP_HOME/share/hadoop/hdfs/*:$HADOOP_HOME/share/hadoop/yarn/lib/*:$HADOOP_HOME/share/hadoop/yarn/*:$HADOOP_HOME/share/hadoop/mapreduce/lib/*:$HADOOP_HOME/share/hadoop/mapreduce/*:$HADOOP_HOME/share/hadoop/tools/lib/*"
ENV PATH $PATH:${SPARK_HOME}/bin:${SPARK_HOME}/sbin
RUN curl -sL --retry 3 \
  "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}.tgz" \
  | gunzip \
  | tar x -C /usr/ \
 && mv /usr/$SPARK_PACKAGE/ $SPARK_HOME \
 && chown -R root:root $SPARK_HOME

# SCALA
ENV SCALA_VERSION_GLOBAL 2.11.7
RUN curl -sL --retry 3 -O "www.scala-lang.org/files/archive/scala-${SCALA_VERSION_GLOBAL}.deb" \
    && dpkg -i "scala-${SCALA_VERSION_GLOBAL}.deb"

ENV SCALA_VERSION 2.11
ENV KAFKA_VERSION 2.4.0
ENV KAFKA_PACKAGE "kafka_${SCALA_VERSION}-${KAFKA_VERSION}"
RUN curl -sL --retry 3 \
    "https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${KAFKA_PACKAGE}.tgz" \
    | gunzip \
    | tar x -C /usr/ \
   && cp -r /usr/${KAFKA_PACKAGE}/* $SPARK_HOME \
   && chown -R root:root ${SPARK_HOME}

EXPOSE 8080
EXPOSE 7077
EXPOSE 3000

#WORKDIR $SPARK_HOME
WORKDIR /app/
VOLUME [ "/app/" ]
CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]