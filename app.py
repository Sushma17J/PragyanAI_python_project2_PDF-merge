import streamlit as st
from pypdf import PdfWriter
from PIL import Image
import tempfile
import os

st.set_page_config(
    page_title="PDF / Image File Merger",
    page_icon="📄"
)

st.title("📄 PDF / Image File Merger")

st.write(
    "Upload multiple PDF or image files and merge them "
    "into a single PDF file."
)

# --------------------------------------
# 1. Upload PDF / Image Files
# --------------------------------------

files = st.file_uploader(
    "Upload PDF / Image Files",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# --------------------------------------
# 2. Display Uploaded Files
# --------------------------------------

if files:

    st.subheader("Uploaded Files")

    for file in files:
        st.write("📄", file.name)

    st.success("Files uploaded successfully!")

# --------------------------------------
# 3. Merge PDF / Image Files
# --------------------------------------

if st.button("Merge PDF / Image Files"):

    if not files:
        st.warning("Please upload PDF or image files first.")

    elif len(files) < 2:
        st.warning("Please upload at least 2 files.")

    else:

        merger = PdfWriter()

        for file in files:

            # Save uploaded file temporarily
            temp_path = os.path.join(
                tempfile.gettempdir(),
                file.name
            )

            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())

            # PDF file
            if file.name.lower().endswith(".pdf"):

                merger.append(temp_path)

            # Image file
            else:

                image = Image.open(temp_path)

                if image.mode != "RGB":
                    image = image.convert("RGB")

                image_pdf = os.path.join(
                    tempfile.gettempdir(),
                    "temp_image.pdf"
                )

                image.save(image_pdf)

                merger.append(image_pdf)

        # Create merged PDF
        output_path = os.path.join(
            tempfile.gettempdir(),
            "merged_file.pdf"
        )

        with open(output_path, "wb") as output:
            merger.write(output)

        merger.close()

        st.success("Files merged successfully!")

        # --------------------------------------
        # 4. Download PDF
        # --------------------------------------

        with open(output_path, "rb") as pdf_file:

            st.download_button(
                label="Download Merged PDF",
                data=pdf_file,
                file_name="merged_file.pdf",
                mime="application/pdf"
            )
