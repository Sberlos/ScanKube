# Copyright 2020 Darkbit.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ruby:2.6.5-alpine3.11

ARG INSPEC_VERSION=4.18.51
ARG GEM_SOURCE=https://rubygems.org
ARG CINC_GEM_SOURCE=https://packagecloud.io/cinc-project/stable
ARG RUNUSER=node
ARG UIDIR="ui"
ARG AUDITDIR="audit"
ARG PROFILEDIR="profiles"

# Deps
RUN apk add --update build-base gcc musl-dev openssl-dev libstdc++ libxml2-dev libffi-dev bash gnupg tar git openssh-client python3-dev python3 py3-pip curl jq && \
    python3 -m pip install --upgrade pip && \
    curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.15.10/2020-02-22/bin/linux/amd64/aws-iam-authenticator && \
    chmod +x ./aws-iam-authenticator && \
    mv ./aws-iam-authenticator /usr/local/bin && \
    rm -rf /tmp/* && \
    rm -rf /var/cache/apk/* && \
    rm -rf /var/tmp/*

# Userland
RUN addgroup -g 1000 ${RUNUSER} && \
    adduser -u 1000 -G ${RUNUSER} -s /bin/sh -D ${RUNUSER}
WORKDIR /home/${RUNUSER}
USER ${RUNUSER}
RUN mkdir -p /home/${RUNUSER}/${UIDIR} /home/${RUNUSER}/${AUDITDIR} /home/${RUNUSER}/${PROFILEDIR}

# Inspec/Cinc
ENV PATH="/home/${RUNUSER}/.gem/ruby/2.6.0/bin:${PATH}"
RUN gem install --user-install --no-document --source ${GEM_SOURCE} --version ${INSPEC_VERSION} inspec && \
    gem install --user-install --no-document --source ${CINC_GEM_SOURCE} --version ${INSPEC_VERSION} cinc-auditor-bin && \
    gem install --user-install --no-document jsonl train-kubernetes && \
    cinc-auditor plugin install train-kubernetes && \
    sed -ie 's#"= 0#"0#g' /home/${RUNUSER}/.inspec/plugins.json

# GCP cli
RUN wget https://dl.google.com/dl/cloudsdk/channels/rapid/google-cloud-sdk.zip -O google-cloud-sdk.zip && \
    unzip google-cloud-sdk.zip && \
    google-cloud-sdk/install.sh --usage-reporting=false --path-update=true --bash-completion=true && \
    google-cloud-sdk/bin/gcloud config set --installation component_manager/disable_update_check true && \
    google-cloud-sdk/bin/gcloud components install kubectl && \
    rm -f google-cloud-sdk/bin/anthoscli && \
    rm -f google-cloud-sdk/bin/kubectl.1.13 && \
    rm -f google-cloud-sdk/bin/kubectl.1.14 && \
    rm -f google-cloud-sdk/bin/kubectl.1.15 && \
    rm -f google-cloud-sdk/bin/kubectl.1.16 && \
    rm -f google-cloud-sdk/bin/kubectl.1.17 && \
    rm -rf google-cloud-sdk.zip

# AWS and Azure cli
ENV PATH="/home/${RUNUSER}/.local/bin:${PATH}"
RUN pip3 install --user awscli
RUN pip3 install --user azure-cli

# Profile versions
ARG K8SPROFILE=0.1.2
ARG GKEPROFILE=0.1.2
ARG AKSPROFILE=0.1.3
ARG EKSPROFILE=0.1.4

# Profiles
RUN wget -O inspec-profile-k8s.zip https://github.com/darkbitio/inspec-profile-k8s/archive/${K8SPROFILE}.zip && \
    unzip inspec-profile-k8s.zip -d /home/${RUNUSER}/${PROFILEDIR} && \
    mv /home/${RUNUSER}/${PROFILEDIR}/inspec-profile-k8s-${K8SPROFILE} /home/${RUNUSER}/${PROFILEDIR}/inspec-profile-k8s && \
    rm inspec-profile-k8s.zip && \
    wget -O inspec-profile-gke.zip https://github.com/darkbitio/inspec-profile-gke/archive/${GKEPROFILE}.zip && \
    unzip inspec-profile-gke.zip -d /home/${RUNUSER}/${PROFILEDIR} && \
    mv /home/${RUNUSER}/${PROFILEDIR}/inspec-profile-gke-${GKEPROFILE} /home/${RUNUSER}/${PROFILEDIR}/inspec-profile-gke && \
    rm inspec-profile-gke.zip && \
    wget -O inspec-profile-aks.zip https://github.com/darkbitio/inspec-profile-aks/archive/${AKSPROFILE}.zip && \
    unzip inspec-profile-aks.zip -d /home/${RUNUSER}/${PROFILEDIR} && \
    mv /home/${RUNUSER}/${PROFILEDIR}/inspec-profile-aks-${AKSPROFILE} /home/${RUNUSER}/${PROFILEDIR}/inspec-profile-aks && \
    rm inspec-profile-aks.zip && \
    wget -O inspec-profile-eks.zip https://github.com/darkbitio/inspec-profile-eks/archive/${EKSPROFILE}.zip && \
    unzip inspec-profile-eks.zip -d /home/${RUNUSER}/${PROFILEDIR} && \
    mv /home/${RUNUSER}/${PROFILEDIR}/inspec-profile-eks-${EKSPROFILE} /home/${RUNUSER}/${PROFILEDIR}/inspec-profile-eks && \
    rm inspec-profile-eks.zip

COPY support /home/${RUNUSER}/${AUDITDIR}/
USER root
RUN chown ${RUNUSER} /home/${RUNUSER}/${AUDITDIR}/*
USER ${RUNUSER}

ENTRYPOINT ["/bin/bash"]
WORKDIR /home/${RUNUSER}/${AUDITDIR}
