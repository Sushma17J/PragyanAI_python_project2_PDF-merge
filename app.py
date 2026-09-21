import streamlit as st
from pypdf import PdfWriter, PdfReader
from PIL import Image
import tempfile
import fitz


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="PDF / Image File Merger",
    page_icon="📄",
    layout="centered"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📄 PDF / Image File Merger")

st.write(
    "Upload PDF or image files, view them, "
    "merge them into one PDF, and download the result."
)


# --------------------------------------------------
# UPLOAD FILES
# --------------------------------------------------

st.subheader("1. Upload PDF / Image Files")

uploaded_files = st.file_uploader(
    "Choose PDF or Image files",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)


# --------------------------------------------------
# UPLOAD STATUS
# --------------------------------------------------

if uploaded_files:

    st.success("✅ Files uploaded successfully!")

else:

    st.info("📂 Please upload PDF or image files.")


# --------------------------------------------------
# REMOVE FILES
# --------------------------------------------------

if uploaded_files:

    if st.button("🗑️ Remove Files"):

        st.session_state.clear()

        st.rerun()


# --------------------------------------------------
# VIEW UPLOADED FILES
# --------------------------------------------------

if uploaded_files:

    st.subheader("2. View Uploaded Files")

    if st.button("👁️ View Files"):

        for file in uploaded_files:

            st.write("---")

            st.write(f"📄 **{file.name}**")


            # --------------------------------------
            # IMAGE FILE
            # --------------------------------------

            if file.name.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):

                image = Image.open(file)

                st.image(
                    image,
                    caption=file.name,
                    use_container_width=True
                )


            # --------------------------------------
            # PDF FILE
            # --------------------------------------

            elif file.name.lower().endswith(".pdf"):

                pdf_bytes = file.getvalue()

                pdf_document = fitz.open(
                    stream=pdf_bytes,
                    filetype="pdf"
                )


                for page_number in range(
                    len(pdf_document)
                ):

                    page = pdf_document[
                        page_number
                    ]

                    pix = page.get_pixmap(
                        matrix=fitz.Matrix(1.5, 1.5)
                    )

                    image_bytes = pix.tobytes(
                        "png"
                    )

                    st.image(
                        image_bytes,
                        caption=f"{file.name} - Page {page_number + 1}",
                        use_container_width=True
                    )


                pdf_document.close()


# --------------------------------------------------
# MERGE FILES
# --------------------------------------------------

st.subheader("3. Merge PDF / Image Files")


if uploaded_files:

    if st.button(
        "🔄 Merge PDF / Image Files",
        type="primary"
    ):

        try:

            # Create output PDF

            output_path = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ).name


            pdf_writer = PdfWriter()


            # --------------------------------------
            # PROCESS EVERY FILE
            # --------------------------------------

            for uploaded_file in uploaded_files:

                file_name = uploaded_file.name.lower()


                # ----------------------------------
                # PDF
                # ----------------------------------

                if file_name.endswith(".pdf"):

                    reader = PdfReader(
                        uploaded_file
                    )

                    for page in reader.pages:

                        pdf_writer.add_page(page)


                # ----------------------------------
                # IMAGE
                # ----------------------------------

                elif file_name.endswith(
                    (".jpg", ".jpeg", ".png")
                ):

                    image = Image.open(
                        uploaded_file
                    ).convert("RGB")


                    image_path = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ).name


                    image.save(
                        image_path,
                        "PDF"
                    )


                    reader = PdfReader(
                        image_path
                    )


                    for page in reader.pages:

                        pdf_writer.add_page(page)


            # --------------------------------------
            # SAVE MERGED PDF
            # --------------------------------------

            with open(
                output_path,
                "wb"
            ) as output_file:

                pdf_writer.write(
                    output_file
                )


            # Save path in session

            st.session_state[
                "merged_pdf"
            ] = output_path


            st.success(
                "✅ Files merged successfully!"
            )


        except Exception as e:

            st.error(
                f"❌ Error: {str(e)}"
            )


# --------------------------------------------------
# MERGED PDF SECTION
# --------------------------------------------------

if "merged_pdf" in st.session_state:

    st.subheader("4. Merged PDF")


    merged_pdf = st.session_state[
        "merged_pdf"
    ]


    # ----------------------------------------------
    # VIEW MERGED PDF
    # ----------------------------------------------

    if st.button("👁️ View Merged PDF"):

        with open(
            merged_pdf,
            "rb"
        ) as pdf_file:

            pdf_bytes = pdf_file.read()


        pdf_document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )


        st.success(
            f"✅ Merged PDF contains {len(pdf_document)} page(s)."
        )


        # Display every page

        for page_number in range(
            len(pdf_document)
        ):

            page = pdf_document[
                page_number
            ]


            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5)
            )


            image_bytes = pix.tobytes(
                "png"
            )


            st.image(
                image_bytes,
                caption=f"Merged PDF - Page {page_number + 1}",
                use_container_width=True
            )


        pdf_document.close()


    # ----------------------------------------------
    # DOWNLOAD MERGED PDF
    # ----------------------------------------------

    with open(
        merged_pdf,
        "rb"
    ) as pdf_file:

        st.download_button(
            label="⬇️ Download Merged PDF",
            data=pdf_file,
            file_name="merged_files.pdf",
            mime="application/pdf"
        )
