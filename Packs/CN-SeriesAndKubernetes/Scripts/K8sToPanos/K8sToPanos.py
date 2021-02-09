import hashlib
import datetime
from dateutil.tz import tzutc


# M4d Propz @Richie
def gen_svc_obj_name(cluster_name, port):
    # service, address, and inbound nat rule object name for K8s service
    #    13 chars  13 chars  4 chars  6 chars   10 chars
    # <namespace>-<svc_name>-<type>-<port_value>-<hash>
    # "kube-system-kube-dns-tgt-53-4e5c971725"
    port_type = ""
    if port["port_type"] == "node_port":
        port_type = "np"
    elif port["port_type"] == "load_balancer":
        port_type = "port"
    elif port["port_type"] == "target_port":
        port_type = "tgt"
    else:
        port_type = "port"
    temp_hash_name = "%s-%s-%s-%s-%s-%s" % (
        cluster_name,
        port["namespace"],
        port["svc_name"],
        port_type,
        port["port"],
        port["protocol"],
    )
    temp_hash_val = hashlib.md5(str(temp_hash_name)).hexdigest()
    hash_val = temp_hash_val[0:10]
    temp_namespace = port["namespace"][0:13]
    temp_svc_name = port["svc_name"][0:13]
    res_name = "%s-%s-%s-%s-%s" % (
        temp_namespace,
        temp_svc_name,
        port_type,
        port["port"],
        hash_val,
    )
    return res_name


def gen_security_policy_rule_name(k8s_rule_name):
    # example : xsoar.k8s.namespace.key-value
    # Longest label supported is 253 + 63 chars or 316
    # https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#syntax-and-character-set
    if len(k8s_rule_name) <= 53:
        return k8s_rule_name
    hex_digest = hashlib.md5(
        k8s_rule_name.encode("utf8")
    ).hexdigest()  # always 32 bytes
    label = k8s_rule_name.split(".")[-1]
    if len(label) <= 30:
        return f"{label}-{hex_digest}"
    return hex_digest


def gen_dag_match_criteria(network_policy, direction, namespace):
    # Extract a list of DAG tags from Network Policy
    tags = []
    if direction == "src":
        try:
            ingress_spec = network_policy["spec"]["ingress"]
            from_ = ingress_spec[0].get("from")
            if not from_:
                from_ = ingress_spec[0]["_from"]
            for selector in from_:
                for k, v in selector.items():
                    if k in ["namespaceSelector", "podSelector"]:
                        if v is not None:
                            labels = v["matchLabels"]
                            for k_, v_ in labels.items():
                                tags.append(f"{namespace}.{k_}.{v_}")
        except KeyError:
            pass
    if direction == "dst":
        try:
            labels = network_policy["spec"]["podSelector"]["matchLabels"]
            for k_, v_ in labels.items():
                tags.append(f"{namespace}.{k_}.{v_}")
        except KeyError:
            pass
    match = " OR ".join(tags)
    return match


def gen_service_objects(network_policy):
    # example : tcp-53
    # Generate service object name from Network Policy "ports"
    services = []
    try:
        ports = network_policy["spec"]["ingress"][0]["ports"]
        for port in ports:
            port_number = port.get("port")
            protocol = port.get("protocol", "tcp").lower()
            name = f"{protocol}-{port_number}"
            services.append({"Name": name, "Port": port_number, "Protocol": protocol})
    except KeyError:
        pass
    return services


def get_ip_blocks(network_policy, direction):
    # example : 192.168.0.0/24
    # Generate CIDR address object from Network Policy
    ip_blocks = []
    if direction == "src":
        try:
            from_ = network_policy["spec"]["ingress"][0]["from"]
            for selector in from_:
                for k, v in selector.items():
                    if k in ["ipBlock"]:
                        cidr = v["cidr"]
                        if isinstance(cidr, list):
                            return cidr
                        else:
                            ip_blocks.append(cidr)
        except KeyError:
            pass
    return ip_blocks


def get_appid(network_policy):
    # example : dns
    # Extract app-id from Network Policy annotations.
    labels = network_policy["metadata"].get("labels")
    if labels:
        appid = labels.get("np.panw.com/appid")
        return appid
    return


def get_vulnerability(network_policy):
    # example : strict
    # Extract vulnerability profile from Network Policy annotations.
    labels = network_policy["metadata"].get("labels")
    if labels:
        vuln_profile = labels.get("np.panw.com/vuln-protection")
        return vuln_profile
    return


def get_antispyware(network_policy):
    # example : strict
    # Extract antispyware profile from Network Policy annotations.
    labels = network_policy["metadata"].get("labels")
    if labels:
        anti_spyware = labels.get("np.panw.com/anti-spyware")
        return anti_spyware
    return


def get_antivirus(network_policy):
    # example : default
    # Extract antivirus profile from Network Policy annotations.
    labels = network_policy["metadata"].get("labels")
    if labels:
        av = labels.get("np.panw.com/antivirus")
        return av
    return


def get_urlfiltering(network_policy):
    # example : default
    # Extract url-filtering profile from Network Policy annotations.
    labels = network_policy["metadata"].get("labels")
    if labels:
        urlfiltering = labels.get("np.panw.com/url-filtering")
        return urlfiltering
    return


def get_fileblocking(network_policy):
    # example : default
    # Extract file-blocking profile from Network Policy annotations.
    labels = network_policy["metadata"].get("labels")
    if labels:
        fb = labels.get("np.panw.com/file-blocking")
        return fb
    return


def get_datafiltering(network_policy):
    # example : default
    # Extract data-filtering profile from Network Policy annotations.
    labels = network_policy["metadata"].get("labels")
    if labels:
        df = labels.get("np.panw.com/data-filtering")
        return df
    return


def get_logprofile(network_policy):
    # example : Panorama
    # Extract log-forwarding profile from Network Policy annotations.
    labels = network_policy["metadata"].get("labels")
    if labels:
        lp = labels.get("np.panw.com/log-profile")
        return lp
    return


# XSOAR Code
def AnalyzePolicy(cluster_name: str, raw_object: dict):

    namespace = raw_object["metadata"]["namespace"]
    policy_name = raw_object["metadata"]["name"]

    # Up to 63 characters total
    namespace = f"{namespace}"
    fqrn = f"{namespace}.{policy_name}"
    rule_name = gen_security_policy_rule_name(fqrn)
    rule_description = f"{fqrn}\n\nThis rule was generated via XSOAR automation and should NOT be edited directly."

    # Get CIDR addresses
    dst_ip_blocks = []  # not currently supporint dst cidr
    src_ip_blocks = get_ip_blocks(raw_object, "src")

    # Generate DAG objects
    src_dag_name = f"{rule_name}.src"
    src_dag_description = fqrn
    src_dag_match = gen_dag_match_criteria(raw_object, "src", namespace)
    src_dag = {}
    if len(src_dag_match) > 0:
        src_dag = {
            "Name": src_dag_name,
            "Match": src_dag_match,
            "Description": src_dag_description,
        }
    dst_dag_name = f"{rule_name}.dst"
    dst_dag_description = fqrn
    dst_dag_match = gen_dag_match_criteria(raw_object, "dst", namespace)
    dst_dag = {}
    if len(dst_dag_match) > 0:
        dst_dag = {
            "Name": dst_dag_name,
            "Match": dst_dag_match,
            "Description": dst_dag_description,
        }

    # Generate service objects
    services = gen_service_objects(raw_object)

    # Get NGFW metadata labels
    appid = get_appid(raw_object)
    vulnerability = get_vulnerability(raw_object)
    antivirus = get_antivirus(raw_object)
    urlfiltering = get_urlfiltering(raw_object)
    fileblocking = get_fileblocking(raw_object)
    datafiltering = get_datafiltering(raw_object)
    logprofile = get_logprofile(raw_object)
    antispyware = get_antispyware(raw_object)

    if len(src_dag_match) > 0:
        src = ", ".join([src_dag_name] + src_ip_blocks)
    else:
        src = ", ".join(src_ip_blocks)

    if len(dst_dag_match) > 0:
        dst = ", ".join([dst_dag_name] + dst_ip_blocks)
    else:
        dst = ", ".join(dst_ip_blocks)

    results = {
        "ConvertedPolicy": {
            "Rule": {
                "Name": rule_name,
                "Service": [
                    service["Name"] for service in services
                ],  # Service object name,
                "FromZone": "any",
                "ToZone": "any",
                "Application": appid,
                "Src": src,
                "Dst": dst,
                "Description": rule_description,
                "VulnerabilityProfile": vulnerability,
                "AntiSpywareProfile": antispyware,
                "AntivirusProfile": antivirus,
                "UrlFilteringProfile": urlfiltering,
                "FileBlockingProfile": fileblocking,
                "DataFilteringProfile": datafiltering,
                "LogProfile": logprofile
            },
            "DAG": [src_dag, dst_dag],
            "Services": services,
        }
    }
    return results


def main():
    arg_network_policy = demisto.args().get("KubernetesNetworkPolicy", "")
    arg_cluster_name = demisto.args().get("ClusterName", "")
    # Some sources provide only the raw_object
    try:
        network_policy = json.loads(arg_network_policy)
    except Exception as e:
        raise

    if network_policy.get("raw_object"):
        network_policy = network_policy.get("raw_object")
    results = AnalyzePolicy(arg_cluster_name, network_policy)

    demisto.results(
        {
            "Type": entryTypes["note"],
            "ContentsFormat": formats["json"],
            "Contents": results,
            "ReadableContentsFormat": formats["json"],
            "HumanReadable": results,
            "EntryContext": results,
        }
    )


if __name__ in ("__main__", "__builtin__", "builtins"):
    main()
