import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label
import xml.etree.ElementTree as ET
import pikepdf
import os
from datetime import datetime
import webbrowser


def create_zugferd_xml(data, filename="zugferd-invoice.xml"):
    invoice = ET.Element("rsm:CrossIndustryInvoice", {
        "xmlns:rsm": "urn:ferd:CrossIndustryDocument:invoice:1p0",
        "xmlns:udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
        "xmlns:qdt": "urn:un:unece:uncefact:data:standard:QualifiedDataType:100",
        "xmlns:ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
    })


    header = ET.SubElement(invoice, "rsm:ExchangedDocument")
    ET.SubElement(header, "ram:ID").text = data["rechnungsnummer"]
    ET.SubElement(header, "ram:IssueDateTime").text = data["datum"]
    ET.SubElement(header, "ram:Name").text = "E-Rechnung"
    ET.SubElement(header, "ram:Information").text = "Copyright by 2025 Markus Begerow - https://linktr.ee/markusbegerow – Alle Rechte vorbehalten"


    trade = ET.SubElement(invoice, "rsm:SupplyChainTradeTransaction")


    agreement = ET.SubElement(trade, "ram:ApplicableHeaderTradeAgreement")

   
    seller = ET.SubElement(agreement, "ram:SellerTradeParty")
    ET.SubElement(seller, "ram:Name").text = data["verkaeufer"]
    seller_address = ET.SubElement(seller, "ram:PostalTradeAddress")
    ET.SubElement(seller_address, "ram:LineOne").text = data["verkaeufer_adresse"]
    ET.SubElement(seller, "ram:SpecifiedTaxRegistration", attrib={"ram:schemeID": "VAT"}).text = data["ust_id"]


    buyer = ET.SubElement(agreement, "ram:BuyerTradeParty")
    ET.SubElement(buyer, "ram:Name").text = data["kaeufer"]
    buyer_address = ET.SubElement(buyer, "ram:PostalTradeAddress")
    ET.SubElement(buyer_address, "ram:LineOne").text = data["kaeufer_adresse"]


    delivery = ET.SubElement(trade, "ram:ApplicableHeaderTradeDelivery")
    ET.SubElement(delivery, "ram:ActualDeliveryDate").text = data["leistungsdatum"]


    settlement = ET.SubElement(trade, "ram:ApplicableHeaderTradeSettlement")
    ET.SubElement(settlement, "ram:PaymentReference").text = data["rechnungsnummer"]
    ET.SubElement(settlement, "ram:PaymentMeansText").text = f"Zahlung bitte an IBAN {data['iban']}, Zahlungsziel: {data['zahlungsziel']}"

    if data.get("steuerbefreit"):
        ET.SubElement(settlement, "ram:TradeTax", attrib={"ram:exemptionReason": data.get("steuerbefreiung_hinweis", "Steuerbefreit")})


    line_item = ET.SubElement(trade, "ram:IncludedSupplyChainTradeLineItem")
    trade_product = ET.SubElement(line_item, "ram:SpecifiedTradeProduct")
    ET.SubElement(trade_product, "ram:Name").text = data["leistungsbeschreibung"]


    monetary = ET.SubElement(trade, "ram:ApplicableHeaderMonetarySummation")
    ET.SubElement(monetary, "ram:LineTotalAmount").text = data["betrag_netto"]
    ET.SubElement(monetary, "ram:TaxTotalAmount").text = data["mwst"]
    ET.SubElement(monetary, "ram:GrandTotalAmount").text = data["betrag_brutto"]

    tree = ET.ElementTree(invoice)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

    return filename


def create_xrechnung_xml(data, filename="xrechnung-invoice.xml"):
    NSMAP = {
        None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    }

    ET.register_namespace('', NSMAP[None])
    ET.register_namespace('cac', NSMAP['cac'])
    ET.register_namespace('cbc', NSMAP['cbc'])

    invoice = ET.Element("Invoice")


    ET.SubElement(invoice, "cbc:CustomizationID").text = "urn:cen.eu:en16931:2017"
    ET.SubElement(invoice, "cbc:ProfileID").text = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"
    ET.SubElement(invoice, "cbc:ID").text = data["rechnungsnummer"]
    ET.SubElement(invoice, "cbc:IssueDate").text = data["datum"]


    supplier = ET.SubElement(invoice, "cac:AccountingSupplierParty")
    party_s = ET.SubElement(supplier, "cac:Party")
    ET.SubElement(party_s, "cbc:EndpointID", schemeID="9930").text = "DE123456789"
    ET.SubElement(party_s, "cbc:Name").text = data["verkaeufer"]
    address_s = ET.SubElement(party_s, "cac:PostalAddress")
    ET.SubElement(address_s, "cbc:StreetName").text = data["verkaeufer_adresse"]
    ET.SubElement(address_s, "cbc:CountrySubentity").text = "DE"
    ET.SubElement(address_s, "cac:Country").append(ET.Element("cbc:IdentificationCode", text="DE"))
    tax_s = ET.SubElement(party_s, "cac:PartyTaxScheme")
    ET.SubElement(tax_s, "cbc:CompanyID").text = data["ust_id"]
    ET.SubElement(tax_s, "cac:TaxScheme").append(ET.Element("cbc:ID", text="VAT"))


    customer = ET.SubElement(invoice, "cac:AccountingCustomerParty")
    party_c = ET.SubElement(customer, "cac:Party")
    ET.SubElement(party_c, "cbc:Name").text = data["kaeufer"]
    address_c = ET.SubElement(party_c, "cac:PostalAddress")
    ET.SubElement(address_c, "cbc:StreetName").text = data["kaeufer_adresse"]
    ET.SubElement(address_c, "cbc:CountrySubentity").text = "DE"
    ET.SubElement(address_c, "cac:Country").append(ET.Element("cbc:IdentificationCode", text="DE"))


    payment = ET.SubElement(invoice, "cac:PaymentMeans")
    ET.SubElement(payment, "cbc:PaymentMeansCode").text = "30"
    ET.SubElement(payment, "cbc:PaymentDueDate").text = data["zahlungsziel"]
    payee = ET.SubElement(payment, "cac:PayeeFinancialAccount")
    ET.SubElement(payee, "cbc:ID").text = data["iban"]

  
    item = ET.SubElement(invoice, "cac:InvoiceLine")
    ET.SubElement(item, "cbc:ID").text = "1"
    ET.SubElement(item, "cbc:InvoicedQuantity", unitCode="C62").text = "1"
    ET.SubElement(item, "cbc:LineExtensionAmount", currencyID="EUR").text = data["betrag_netto"]

    tax_total = ET.SubElement(item, "cac:TaxTotal")
    ET.SubElement(tax_total, "cbc:TaxAmount", currencyID="EUR").text = data["mwst"]

    tax_sub = ET.SubElement(tax_total, "cac:TaxSubtotal")
    ET.SubElement(tax_sub, "cbc:TaxableAmount", currencyID="EUR").text = data["betrag_netto"]
    ET.SubElement(tax_sub, "cbc:TaxAmount", currencyID="EUR").text = data["mwst"]
    tax_cat = ET.SubElement(tax_sub, "cac:TaxCategory")
    ET.SubElement(tax_cat, "cbc:ID").text = "S"
    ET.SubElement(tax_cat, "cbc:Percent").text = "19"
    ET.SubElement(tax_cat, "cac:TaxScheme").append(ET.Element("cbc:ID", text="VAT"))

    prod = ET.SubElement(item, "cac:Item")
    ET.SubElement(prod, "cbc:Name").text = data["leistungsbeschreibung"]

    price = ET.SubElement(item, "cac:Price")
    ET.SubElement(price, "cbc:PriceAmount", currencyID="EUR").text = data["betrag_netto"]


    monetary = ET.SubElement(invoice, "cac:LegalMonetaryTotal")
    ET.SubElement(monetary, "cbc:LineExtensionAmount", currencyID="EUR").text = data["betrag_netto"]
    ET.SubElement(monetary, "cbc:TaxExclusiveAmount", currencyID="EUR").text = data["betrag_netto"]
    ET.SubElement(monetary, "cbc:TaxInclusiveAmount", currencyID="EUR").text = data["betrag_brutto"]
    ET.SubElement(monetary, "cbc:PayableAmount", currencyID="EUR").text = data["betrag_brutto"]

    tree = ET.ElementTree(invoice)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    return filename


def create_pdfa3_xmp_metadata():
    return b'''<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Python PikePDF">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
           xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/"
           xmlns:dc="http://purl.org/dc/elements/1.1/"
           xmlns:xmp="http://ns.adobe.com/xap/1.0/"
           xmlns:pdf="http://ns.adobe.com/pdf/1.3/">
    <rdf:Description rdf:about="">
      <pdfaid:part>3</pdfaid:part>
      <pdfaid:conformance>B</pdfaid:conformance>
      <pdf:Producer>Python PikePDF</pdf:Producer>
      <xmp:CreatorTool>ZUGFeRD E-Rechnung Generator</xmp:CreatorTool>
      <dc:title>
        <rdf:Alt>
          <rdf:li xml:lang="x-default">ZUGFeRD Rechnung</rdf:li>
        </rdf:Alt>
      </dc:title>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>'''


def embed_zugferd_to_pdf(pdf_path, xml_path, output_path, icc_profile="sRGB.icc"):
    with pikepdf.Pdf.open(pdf_path) as pdf:
        with open(xml_path, "rb") as f:
            xml_data = f.read()

        embedded_file_stream = pikepdf.Stream(pdf, xml_data)
        embedded_file_stream.Type = pikepdf.Name("/EmbeddedFile")
        embedded_file_stream[pikepdf.Name("/Subtype")] = pikepdf.Name("/application/xml")
        embedded_file_stream_obj = pdf.make_indirect(embedded_file_stream)

        ef_dict = pikepdf.Dictionary()
        ef_dict[pikepdf.Name("/F")] = embedded_file_stream_obj

        filespec_dict = pikepdf.Dictionary()
        filespec_dict[pikepdf.Name("/Type")] = pikepdf.Name("/Filespec")
        filespec_dict[pikepdf.Name("/F")] = pikepdf.String(os.path.basename(xml_path))
        filespec_dict[pikepdf.Name("/UF")] = pikepdf.String(os.path.basename(xml_path))
        filespec_dict[pikepdf.Name("/EF")] = ef_dict
        filespec_dict[pikepdf.Name("/AFRelationship")] = pikepdf.Name("/Data")
        filespec_dict[pikepdf.Name("/Desc")] = pikepdf.String("ZUGFeRD XML file")

        filespec = pdf.make_indirect(filespec_dict)

        if "/Names" not in pdf.Root:
            pdf.Root.Names = pdf.make_indirect(pikepdf.Dictionary())
        pdf.Root.Names.EmbeddedFiles = pdf.make_indirect(pikepdf.Dictionary({
            "/Names": [pikepdf.String(os.path.basename(xml_path)), filespec]
        }))
        pdf.Root.AF = [filespec]

        with open(icc_profile, "rb") as icc_file:
            icc_data = icc_file.read()
        icc_stream = pikepdf.Stream(pdf, icc_data)
        icc_stream_obj = pdf.make_indirect(icc_stream)

        output_intent = pikepdf.Dictionary({
            "/Type": pikepdf.Name("/OutputIntent"),
            "/S": pikepdf.Name("/GTS_PDFA1"),
            "/OutputConditionIdentifier": pikepdf.String("sRGB IEC61966-2.1"),
            "/Info": pikepdf.String("sRGB"),
            "/DestOutputProfile": icc_stream_obj
        })

        pdf.Root.OutputIntents = [pdf.make_indirect(output_intent)]
        xmp_data = create_pdfa3_xmp_metadata()
        pdf.Root.Metadata = pikepdf.Stream(pdf, xmp_data)
        pdf.Root.Version = pikepdf.Name("/1.7")
        pdf.save(output_path)


class ZugferdApp:
    def __init__(self, root):
        self.root = root


        self.root.title("ZUGFeRD/XRechnung E-Rechnung Generator by Markus Begerow")

        self.pdf_path = ""

        self.fields = {
            "rechnungsnummer": tk.StringVar(),
            "datum": tk.StringVar(value=datetime.today().strftime("%d.%m.%Y")),
            "leistungsdatum": tk.StringVar(),
            "verkaeufer": tk.StringVar(),
            "verkaeufer_adresse": tk.StringVar(),
            "ust_id": tk.StringVar(),
            "kaeufer": tk.StringVar(),
            "kaeufer_adresse": tk.StringVar(),
            "leistungsbeschreibung": tk.StringVar(),
            "betrag_netto": tk.StringVar(),
            "mwst": tk.StringVar(),
            "betrag_brutto": tk.StringVar(),
            "iban": tk.StringVar(),
            "zahlungsziel": tk.StringVar(),
            "steuerbefreiung_hinweis": tk.StringVar()
        }

        self.label_names = {
            "rechnungsnummer": "Rechnungsnummer:",
            "datum": "Datum:",
            "leistungsdatum": "Leistungsdatum:",
            "verkaeufer": "Verkäufer:",
            "verkaeufer_adresse": "Verkäuferadresse:",
            "ust_id": "USt-ID:",
            "kaeufer": "Käufer",
            "kaeufer_adresse": "Käuferadresse:",
            "leistungsbeschreibung": "Leistungsbeschreibung:",
            "betrag_netto": "Betrag netto:",
            "mwst": "MwSt:",
            "betrag_brutto": "Gesamtbetrag (Brutto):",
            "iban": "IBAN:",
            "zahlungsziel": "Zahlungsziel:",
            "steuerbefreiung_hinweis": "Hinweis zur Steuerbefreiung:"
        }


        self.steuerbefreit = tk.BooleanVar()

        row = 1
        for label, var in self.fields.items():
            label_text = self.label_names.get(label, label.replace("_", " ").capitalize())
            tk.Label(root, text=label_text).grid(row=row, column=0, sticky="w", padx=5)
            entry = tk.Entry(root, textvariable=var)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            row += 1

        tk.Checkbutton(root, text="Steuerbefreit gemäß §19 UStG", variable=self.steuerbefreit).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1

        tk.Button(root, text="PDF auswählen", command=self.select_pdf).grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(root, text="ZUGFeRD erzeugen", command=self.generate_invoice).grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        row += 1
        tk.Button(root, text="XRechnung / PEPPOL exportieren", command=self.generate_xrechnung).grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        row += 1
        tk.Button(root, text="Info & Support", command=show_info).grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)


    def select_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.pdf_path:
            messagebox.showinfo("Datei gewählt", f"PDF: {self.pdf_path}")

    def generate_invoice(self):
        if not self.pdf_path:
            messagebox.showerror("Fehler", "Bitte wähle eine PDF-Rechnung aus.")
            return

        data = {key: var.get() for key, var in self.fields.items()}
        data["steuerbefreit"] = self.steuerbefreit.get()

        xml_path = os.path.splitext(self.pdf_path)[0] + "_zugferd-invoice.xml"
        output_pdf = os.path.splitext(self.pdf_path)[0] + "_ZUGFeRD.pdf"

        create_zugferd_xml(data, xml_path)
        embed_zugferd_to_pdf(self.pdf_path, xml_path, output_pdf)

        messagebox.showinfo("Fertig", f"ZUGFeRD-PDF erzeugt:\n{output_pdf}")

    def generate_xrechnung(self):
        data = {key: var.get() for key, var in self.fields.items()}
        xrechnung_path = os.path.splitext(self.pdf_path)[0] + "_xrechnung-invoice.xml"
        create_zugferd_xml(data, xrechnung_path)
        messagebox.showinfo("XRechnung", f"XRechnung XML-Datei erzeugt:\n{xrechnung_path}")

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, wraplength=300)
        label.pack()
    
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def center_window(win, width, height):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")




def show_splash(root):
    splash = Toplevel()
    splash.overrideredirect(True)
    center_window(splash, 400, 100)
    Label(splash, text="ZUGFeRD/XRechnung E-Rechnung Generator wird geladen …", font=("Arial", 10)).pack(expand=True)
    root.after(1500, splash.destroy)


import tkinter as tk
import webbrowser

def show_info():
    info = tk.Toplevel()
    info.title("Info")
    info.geometry("360x160")
    center_window(info, 360, 250)
    info.resizable(False, False)

    tk.Label(info, text="ZUGFeRD/XRechnung E-Rechnung Generator", font=("Arial", 10, "bold")).pack(pady=(10, 0))

    tk.Label(info, text="Copyright by 2025 Markus Begerow").pack()


    link1 = tk.Label(info, text="🔗 linktr.ee/markusbegerow", fg="blue", cursor="hand2")
    link1.pack()
    link1.bind("<Button-1>", lambda e: webbrowser.open_new("https://linktr.ee/markusbegerow"))


    link2 = tk.Label(info, text="❤️ Jetzt unterstützen via PayPal", fg="blue", cursor="hand2")
    link2.pack()
    link2.bind("<Button-1>", lambda e: webbrowser.open_new("https://paypal.me/MarkusBegerow?country.x=DE&locale.x=de_DE"))

 
    disclaimer = (
        "Die Nutzung dieses Tools erfolgt auf eigene Verantwortung.\n"
        "Es wird keine Haftung für Richtigkeit, Vollständigkeit oder\n"
        "rechtliche Konformität übernommen.\n\n"
        "Keine Rechts- oder Steuerberatung.\nKeine Gewährleistung."
    )
    tk.Label(info, text=disclaimer, wraplength=360, justify="center", fg="gray").pack(padx=10, pady=(0, 10))

    tk.Button(info, text="Schließen", command=info.destroy).pack(pady=5)



if __name__ == "__main__":
    root = tk.Tk()
    center_window(root, 700, 500)
    root.withdraw() 
    show_splash(root)

    def start_main():
        root.deiconify()  
        app = ZugferdApp(root)

    root.after(1600, start_main)  
    root.mainloop()
