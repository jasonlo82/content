This Playbook simulates a vulnerability scan using the "HelloWorld" sample integration. It's used to demonstrate how to use the GenericPolling mechanism to run jobs that take several seconds or minutes to complete. It is designed to be used as a subplaybook, but you can also use it as a standalone playbook, by providing the ${Endpoint.Hostname} input in the Context.

Other inputs include the report output format (JSON context or File attached), and the Interval/Timeouts to use for polling the scan status until it's complete.

## Dependencies
This playbook uses the following sub-playbooks, integrations, and scripts.

### Sub-playbooks
* GenericPolling

### Integrations
* HelloWorldV2

### Scripts
* PrintErrorEntry

### Commands
* helloworld-say-hello-new
* helloworld-get-alert-new

## Playbook Inputs
---

| **Name** | **Description** | **Default Value** | **Required** |
| --- | --- | --- | --- |
| Hostname | Hostname to run the scan against. By default takes $\{Endpoint.Hostname\} from the context as the input. | ${Endpoint.Hostname} | Required |
| Report Format | Output report format: can be "json" \(output parsed and written in the Context\) or "file" \(saved as an attachment\). By default is "json". | json | Required |
| Interval | How often to check for the scan to be completed \(minutes\) | 1 | Required |
| Timeout | How long to wait for the scan to be completed before timing out \(minutes\) | 15 | Required |

## Playbook Outputs
---

| **Path** | **Description** | **Type** |
| --- | --- | --- |
| HelloWorld.Scan.entity.entity-id | Scanned entity ID. | unknown |
| HelloWorld.Scan.entity.ip_address | Scanned entity IP address. | unknown |
| HelloWorld.Scan.entity.type | Scanned entity type. | unknown |
| HelloWorld.Scan.entity.vulnerability_status | Scanned entity vulnerability status. | unknown |
| HelloWorld.Scan.entity.vulns | Scanned entity CVE. | unknown |
| CVE.ID | The ID of the CVE. | unknown |
| InfoFile.EntryID | The EntryID of the report file. | unknown |
| InfoFile.Extension | The extension of the report file. | unknown |
| InfoFile.Name | The name of the report file. | unknown |
| InfoFile.Info | The info of the report file. | unknown |
| InfoFile.Size | The size of the report file. | unknown |
| InfoFile.Type | The type of the report file. | unknown |

## Playbook Image
---
![HelloWorld Say Hello](Insert the link to your image here)