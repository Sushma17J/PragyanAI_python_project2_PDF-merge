import streamlit as st
from pypdf import PdfWriter
from PIL import Image
import tempfile
import os
import base64

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

    st.success("Files uploaded successfully!")

    if st.button("View Uploaded Files"):

        st.subheader("Uploaded Files")

        for file in files:
            st.write("📄", file.name)

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

            # Create temporary path
            temp_path = os.path.join(
                tempfile.gettempdir(),
                file.name
            )

            # Save uploaded file
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())

            # -------------------------------
            # PDF File
            # -------------------------------

            if file.name.lower().endswith(".pdf"):

                merger.append(temp_path)

            # -------------------------------
            # Image File
            # -------------------------------

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

        # --------------------------------------
        # Create Merged PDF
        # --------------------------------------

        output_path = os.path.join(
            tempfile.gettempdir(),
            "merged_file.pdf"
        )

        with open(output_path, "wb") as output:

            merger.write(output)

        merger.close()

        st.success("Files merged successfully!")

        # Store path in session state
        st.session_state["merged_pdf"] = output_path


# --------------------------------------
# 4. View Merged PDF
# --------------------------------------

if "merged_pdf" in st.session_state:

    if st.button("View Merged PDF"):

        with open(
            st.session_state["merged_pdf"],
            "rb"
        ) as pdf_file:

            pdf_bytes = pdf_file.read()

        base64_pdf = base64.b64encode(
            pdf_bytes
        ).decode("utf-8")

        pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="600"
            type="application/pdf">
        </iframe>
        """

        st.markdown(
            pdf_display,
            unsafe_allow_html=True
        )


# --------------------------------------
# 5. Download Merged PDF
# --------------------------------------

if "merged_pdf" in st.session_state:

    with open(
        st.session_state["merged_pdf"],
        "rb"
    ) as pdf_file:

        st.download_button(
            label="Download Merged PDF",
            data=pdf_file,
            file_name="merged_file.pdf",
            mime="application/pdf"
        )
