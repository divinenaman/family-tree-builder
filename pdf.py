
from PyPDF2 import PdfFileReader
import os
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract
import cv2
import image_processing
import numpy as np


def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    txt = f"""
    Information about {pdf_path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """

    print(information)
    return information


def pdf_as_image_crops(pdf_path, show=False):
    images = pdf_to_image(pdf_path)
    images = list(map(lambda x: np.array(x), images))

    img_crops = []
    for img in images[2:len(images) - 1]:
        horizontal, vertical = image_processing.detect_lines(
            img, minLinLength=350, display=False, write=False)

        if len(horizontal) < 2 or len(vertical) < 2:
            continue

        for h in range(0, len(horizontal) - 1):
            for v in range(0, len(vertical)-1):


                img_crop_1, img_crop_2 = image_processing.get_info_box(
                    img, horizontal[h], horizontal[h+1], vertical[v], vertical[v+1])

                gry_1 = cv2.cvtColor(img_crop_1, cv2.COLOR_BGR2GRAY)
                thresh_1 = cv2.threshold(gry_1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                # Invert and perform text extraction
                thresh_1 = 255 - thresh_1

                gry_2 = cv2.cvtColor(img_crop_2, cv2.COLOR_BGR2GRAY)
                thresh_2 = cv2.threshold(gry_2, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                # Invert and perform text extraction
                thresh_2 = 255 - thresh_2

                img_crops.append((thresh_1, thresh_2))
                
                #cv2.imwrite("tmp/imagesCropped/test5.jpg", cv2.cvtColor(img_crop_2, cv2.COLOR_BGR2GRAY))

    #cv2.imwrite("tmp/imagesCropped/test2.jpg", img_crops[1])

    if (show):
        cv2.imshow("crop", img_crops[1])
        cv2.waitKey(0)

    return img_crops


def pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path)
    return images


if __name__ == "__main__":

    pdf_path = os.path.join("tmp", "PopupCaptcha.pdf")

    #extract_information(os.path.join("tmp", "PopupCaptcha.pdf"))

    #text = extract_text('tmp/PopupCaptcha.pdf')
    # print(text)

    # from io import StringIO

    # from pdfminer.converter import TextConverter
    # from pdfminer.layout import LAParams
    # from pdfminer.pdfdocument import PDFDocument
    # from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    # from pdfminer.pdfpage import PDFPage
    # from pdfminer.pdfparser import PDFParser

    # output_string = StringIO()
    # with open('tmp/PopupCaptcha.pdf', 'rb') as in_file:
    #     parser = PDFParser(in_file)
    #     doc = PDFDocument(parser)
    #     rsrcmgr = PDFResourceManager()
    #     device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    #     interpreter = PDFPageInterpreter(rsrcmgr, device)
    #     for page in PDFPage.create_pages(doc):
    #         interpreter.process_page(page)

    # print(output_string.getvalue())

    # pdf_to_image(pdf_path)

    # t = pytesseract.image_to_string("tmp/page2.jpg")

    # print(t)

    pdf_as_image_crops("tmp/PopupCaptcha.pdf")
