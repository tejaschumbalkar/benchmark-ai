import logging

import kubernetes
from kubernetes.client import V1PodList, V1PersistentVolumeClaimList
from time import sleep
from timeout_decorator import timeout

from bai_k8s_utils.service_labels import ServiceLabels

logger = logging.getLogger(__name__)


class KubernetesTestUtilsClient:
    # Utilities to use in integration tests.
    # All of them expect pod to be at least in Pending state.
    # So no super long timeouts are necessary for any environment
    # Although we seen 10 seconds to be not enough to _terminate_ the pod
    def __init__(self, api_client: kubernetes.client.ApiClient, service: str):
        self.batch_api_instance = kubernetes.client.BatchV1Api(api_client)
        self.core_api_instance = kubernetes.client.CoreV1Api(api_client)
        self.service = service

    DEFAULT_TIMEOUT_SECONDS = 30

    def is_pod_present(self, namespace: str, client_id: str, action_id: str):
        label_selector = ServiceLabels.get_label_selector(self.service, client_id, action_id)
        logger.info(f"pod selector request:{label_selector}")
        pods: V1PodList = self.core_api_instance.list_namespaced_pod(namespace, label_selector=label_selector)
        return bool(pods.items)

    def is_job_present(self, namespace: str, client_id: str, action_id: str):
        label_selector = ServiceLabels.get_label_selector(self.service, client_id, action_id)
        logger.info(f"job selector request:{label_selector}")
        pods: V1PodList = self.batch_api_instance.list_namespaced_job(namespace, label_selector=label_selector)
        return bool(pods.items)

    def is_volume_claim_present(self, namespace: str, client_id: str, action_id: str):
        label_selector = ServiceLabels.get_label_selector(self.service, client_id, action_id)
        logger.info(f"volume claim selector request:{label_selector}")
        pods: V1PersistentVolumeClaimList = self.core_api_instance.list_namespaced_persistent_volume_claim(
            namespace, label_selector=label_selector
        )
        return bool(pods.items)

    @timeout(DEFAULT_TIMEOUT_SECONDS)
    def wait_for_volume_claim_exists(self, namespace: str, client_id: str, action_id: str):
        while not self.is_volume_claim_present(namespace, client_id, action_id):
            logger.info("volume claim doesn't exist yet")
            sleep(1)

    @timeout(DEFAULT_TIMEOUT_SECONDS)
    def wait_for_volume_claim_not_exists(self, namespace: str, client_id: str, action_id: str):
        while self.is_volume_claim_present(namespace, client_id, action_id):
            logger.info("volume claim still exists")
            sleep(1)

    @timeout(DEFAULT_TIMEOUT_SECONDS)
    def wait_for_pod_exists(self, namespace: str, client_id: str, action_id: str):
        while not self.is_pod_present(namespace, client_id, action_id):
            logger.info("pod doesn't exist yet")
            sleep(1)

    @timeout(DEFAULT_TIMEOUT_SECONDS)
    def wait_for_pod_not_exists(self, namespace: str, client_id: str, action_id: str):
        while self.is_pod_present(namespace, client_id, action_id):
            logger.info("pod still exists")
            sleep(1)

    @timeout(DEFAULT_TIMEOUT_SECONDS)
    def wait_for_job_exists(self, namespace: str, client_id: str, action_id: str):
        while not self.is_job_present(namespace, client_id, action_id):
            logger.info("job doesn't exist yet")
            sleep(1)

    @timeout(DEFAULT_TIMEOUT_SECONDS)
    def wait_for_job_not_exists(self, namespace: str, client_id: str, action_id: str):
        while self.is_job_present(namespace, client_id, action_id):
            logger.info("job still exists")
            sleep(1)
