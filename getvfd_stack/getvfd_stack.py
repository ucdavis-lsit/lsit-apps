from aws_cdk import Stack
from constructs import Construct
from aws_cdk.aws_elasticloadbalancingv2 import ListenerAction, ListenerCondition, ApplicationListenerRule, ListenerCertificate

class GetVFDStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, app_props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Required props
        app_name = app_props["app_name"]
        app_env = app_props["app_env"]
        host_headers = app_props["host_headers"]
        certificate_arns = app_props["certificate_arns"]
        self.https_listener = app_props["https_listener"]
        self.http_listener = app_props["http_listener"]
        https_load_balancer_priority = app_props["https_load_balancer_priority"]
        http_load_balancer_priority = app_props["http_load_balancer_priority"]
        
        # Calculated props
        app_prefix = app_name.capitalize() + app_env.capitalize()
   
        certificates = []
        for certificate_arn in certificate_arns:
            certificates.append(
                ListenerCertificate(
                    certificate_arn
                )
            )

        self.https_listener.add_certificates(
            "{app_prefix}Certtificates".format(app_prefix=app_prefix),
            certificates
        )
        
        

        listener_action_json = {
            "redirectConfig" : {
                "port" : "443",
                "statusCode" : "HTTP_301",
                "host": "getvfd.vercel.app",
            },
            "type" : "redirect"
        }     

        ApplicationListenerRule(
            self,
            "{app_prefix}HttpsListenerRule".format(app_prefix=app_prefix),
            listener=self.https_listener,
            conditions=[ListenerCondition.host_headers(host_headers)],
            priority=https_load_balancer_priority,
            action=ListenerAction(listener_action_json)
        )

        ApplicationListenerRule(
            self,
            "{app_prefix}HttpListenerRule".format(app_prefix=app_prefix),
            listener=self.http_listener,
            conditions=[ListenerCondition.host_headers(host_headers)],
            priority=http_load_balancer_priority,
            action=ListenerAction(listener_action_json)
        )
