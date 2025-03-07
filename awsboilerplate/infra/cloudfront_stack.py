from aws_cdk import (
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
    aws_route53 as route53,
    aws_certificatemanager as certificatemanager,
    aws_apigateway,
    core,
    aws_route53,
    aws_route53_patterns,
    aws_route53_targets,
    aws_s3_deployment as s3deploy,
    aws_iam as iam,
    aws_codepipeline as code_pipeline
)
import os

from aws_cdk.aws_s3_deployment import CacheControl


class FlexibleCloudFrontStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain_name, hosted_zone_id, **kwargs):
        super().__init__(scope, id, **kwargs)
        # bucket
        # deployment
        # source config
        # www distribution
        # api gateway
        # ----- if a domain is supplied
        # hosted zone
        # certificate
        # alias
        # arecord cloudfront
        # redirect
        # arecord apigateway

        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "HostedZone",
                                                                         hosted_zone_id=hosted_zone_id,
                                                                         zone_name=domain_name)

        # SSL/TLS Certificate
        # https://github.com/aws/aws-cdk/pull/8552
        # Experimental vs 'Certificate' (which requires validation in the console)
        tls_cert = certificatemanager.DnsValidatedCertificate(
            self,
            "SiteCertificate",
            hosted_zone=hosted_zone,
            domain_name=f'*.{domain_name}',
            subject_alternative_names=[domain_name],
            region='us-east-1',
        )

        self.www_site_bucket = s3.Bucket(
            self,
            f'WWW2_Bucket_{domain_name}',
            bucket_name=domain_name,
            website_index_document='index.html',
            website_error_document='index.html',
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # CloudFront distribution that provides HTTPS - for www
        www_alias_configuration = cloudfront.AliasConfiguration(
            acm_cert_ref=tls_cert.certificate_arn,
            names=[f'www.{domain_name}'],
            ssl_method=cloudfront.SSLMethod.SNI,
            security_policy=cloudfront.SecurityPolicyProtocol.TLS_V1_1_2016
        )

        www_source_configuration = cloudfront.SourceConfiguration(
            s3_origin_source=cloudfront.S3OriginConfig(
                s3_bucket_source=self.www_site_bucket
            ),
            behaviors=[cloudfront.Behavior(is_default_behavior=True)]
        )

        www_distribution = cloudfront.CloudFrontWebDistribution(
            self,
            'SiteDistribution',
            alias_configuration=www_alias_configuration, #This as added
            origin_configs=[www_source_configuration]
        )

        s3deploy.BucketDeployment(self, "DeployWebsite",
            sources=[s3deploy.Source.asset(os.path.abspath("awsboilerplate/www/build"))],
            destination_bucket=self.www_site_bucket,
            distribution=www_distribution)
            # cache_control = [CacheControl.from_string("max-age=0,no-cache,no-store,must-revalidate")])

        route53.ARecord(
            self,
            'CloudFrontARecord',
            zone=hosted_zone,
            record_name=f'www.{domain_name}',  # site domain
            target=aws_route53.RecordTarget.from_alias(aws_route53_targets.CloudFrontTarget(www_distribution))
        )


        # NAKED site bucket which redirects to naked to www
        redirect = aws_route53_patterns.HttpsRedirect(self, 'NakedRedirect',
                                                      record_names=[domain_name],
                                                      target_domain=f'www.{domain_name}',
                                                      zone=hosted_zone,
                                                      certificate=tls_cert)

        # API Gateway
        self.rest_api = aws_apigateway.RestApi(self, 'RestApiGateway', deploy=False)
        api_domain_name = f'api.{domain_name}'
        domain = self.rest_api.add_domain_name('APIDomain', certificate=tls_cert, domain_name=api_domain_name)

        route53.ARecord(
            self,
            'APIGWAliasRecord',
            zone=hosted_zone,
            record_name=api_domain_name,  # site domain
            target=aws_route53.RecordTarget.from_alias(aws_route53_targets.ApiGatewayDomain(domain))
        )


class APIGatewayDeployStack(core.Stack):
    '''
    When breaking up API GW between stacks the pattern is to add a stack at the end of the stage to finalize deployment
    https://docs.aws.amazon.com/cdk/api/latest/docs/aws-apigateway-readme.html#breaking-up-methods-and-resources-across-stacks
    '''
    def __init__(self, scope: core.Construct, id: str, api_gateway: aws_apigateway.RestApi, **kwargs):
        super().__init__(scope, id, **kwargs)
        deployment = aws_apigateway.Deployment(self, 'APIGWDeployment', api=api_gateway)
        map(lambda m: deployment.node.add_dependency(m), api_gateway.methods)
        stage = aws_apigateway.Stage(self, 'Stage', deployment=deployment, stage_name='prod')