import os, argparse, openssh_wrapper
from proxmoxer import ProxmoxAPI
from tempfile import NamedTemporaryFile
from datetime import datetime
from requests.structures import CaseInsensitiveDict
from http.client import HTTPConnection
from dateutil.relativedelta import relativedelta
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice


def generate_invoice(client,provider_name,filename,date, host, user, password):
    os.environ["INVOICE_LANG"] = "fr"
    # 730 hours per month =  2628000
    seconds_per_month = 2628000
    client = Client(client)
    provider = Provider(summary=provider_name,bank_account='000000000', bank_code='0000')
    creator = Creator(provider_name)

    invoice = Invoice(client, provider, creator)
    invoice.number = date
    invoice.currency = u'\u20ac'
    invoice.currency_locale = 'fr_FR.UTF-8'
    proxmox = ProxmoxAPI(
        host, user=user, password=password, verify_ssl=False
    )
    for node in proxmox.nodes.get():
        node_cpu = node["maxcpu"]
        node_tdp = 65
        node_disk = node["maxdisk"]
        node_ram = node["mem"]        
        for vm in proxmox.nodes(node["node"]).qemu.get():
            if not (vm["tags"]) == "template" :       
                vm_name = vm["name"]
                vm_id = str(vm["vmid"])
                vm_uptime = vm["uptime"]
                vm_uptime = (vm_uptime / seconds_per_month)
                vm_status = vm["status"]
                vm_cpu = vm["cpu"]
                vm_cpu = (vm_cpu) * vm_uptime                
                vm_ram = vm["maxmem"]
                vm_ram = (vm_ram / 1024 / 1024 / 1024) * vm_uptime
                vm_netout = vm["netout"]
                vm_netout = (vm_netout / 1024 / 1024 / 1024)
                vm_netin = vm["netin"]
                vm_netin = (vm_netin / 1024 / 1024 / 1024)          
                vm_storage = vm["maxdisk"]
                vm_storage = (vm_storage / 1024 / 1024 / 1024)
                vm_consumption = (vm_uptime / node_tdp) * node_tdp
                description = vm_id + " - " + vm_name + " - CPU"                        
                invoice.add_item(Item(vm_cpu, 7, description=description, unit="CPU"))
                description = vm_id + " - " + vm_name  + " - RAM"                    
                invoice.add_item(Item(vm_ram, 7, description=description, unit="GB"))
                description = vm_id + " - " + vm_name  + " - NETOUT"                    
                invoice.add_item(Item(vm_netout,0.01, description=description, unit="GB", tax=0))
                description = vm_id + " - " + vm_name  + " - NETIN"                    
                invoice.add_item(Item(vm_netin,0.01, description=description, unit="GB", tax=0))
                description = vm_id + " - " + vm_name  + " - STORAGE"                    
                invoice.add_item(Item(vm_storage,0.04, description=description, unit="GB", tax=0))   
                description = vm_id + " - " + vm_name  + " - CONSUMPTION"                    
                invoice.add_item(Item(vm_consumption,0.00015, description=description, unit='W', tax=0)) 
    generate_pdf(invoice,filename)

def generate_pdf(invoice, filename):
    pdf = SimpleInvoice(invoice)
    pdf.gen(filename, generate_qr_code=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=False, type=str, default="Client")
    parser.add_argument("--provider_name", required=False, type=str, default="Provider")
    parser.add_argument("--filename", required=False, type=str, help='Euro', default="invoice.pdf")
    parser.add_argument("--host", required=False, type=str, help='IP or Hostname', default="192.168.1.1")
    parser.add_argument("--user", required=False, type=str, help='root@pam', default="root@pam")        
    default_date = datetime.now()-relativedelta(months=1)
    default_date = default_date.strftime("%Y%m")
    parser.add_argument("--date", required=False, type=str, help='Date: year-month', default=default_date)
    # Parse args
    args = parser.parse_args()
    client = args.client
    provider_name = args.provider_name
    date= args.date   
    filename= args.filename  
    host= args.host
    user = args.user
    if os.environ.get('PROXMOX_PASSWORD') is not None:
        password = os.environ.get('PROXMOX_PASSWORD')
        generate_invoice(client,provider_name,filename,date, host, user, password)    
    else:
        print("Proxmox Password not found in env variable")    
if __name__ == "__main__":
    main()