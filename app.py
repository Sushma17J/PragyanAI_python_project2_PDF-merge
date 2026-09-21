import streamlit as st
from pypdf import PdfWriter, PdfReader
from PIL import Image
import tempfile
import fitz


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="PDF / Image File Merger",
    page_icon="📄",
    layout="centered"
)


# ==================================================
# SESSION STATE
# ==================================================

if "file_order" not in st.session_state:
    st.session_state.file_order = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "merged_pdf" not in st.session_state:
    st.session_state.merged_pdf = None


# ==================================================
# TITLE
# ==================================================

st.title("📄 PDF / Image File Merger")

st.write(
    "Upload PDF or image files, arrange their order, "
    "view them, merge them, and download the final PDF."
)


# ==================================================
# UPLOAD FILES
# ==================================================

st.subheader("1. Upload PDF / Image Files")

uploaded_files = st.file_uploader(
    "Choose PDF or Image files",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)


# ==================================================
# CREATE FILE DICTIONARY
# ==================================================

if uploaded_files:

    current_files = {}

    for file in uploaded_files:

        file_key = f"{file.name}_{file.size}"

        current_files[file_key] = file


    # Remove files that no longer exist
    st.session_state.file_order = [
        key
        for key in st.session_state.file_order
        if key in current_files
    ]


    # Add newly uploaded files at the end
    for key in current_files:

        if key not in st.session_state.file_order:

            st.session_state.file_order.append(key)


    # Create files in selected order
    ordered_files = [
        current_files[key]
        for key in st.session_state.file_order
    ]


    st.success(
        f"✅ {len(ordered_files)} file(s) uploaded successfully!"
    )


else:

    ordered_files = []

    st.info("📂 Please upload PDF or image files.")


# ==================================================
# REMOVE FILES
# ==================================================

if uploaded_files:

    if st.button(
        "🗑️ Remove All Files",
        type="secondary"
    ):

        st.session_state.file_order = []

        st.session_state.merged_pdf = None

        st.session_state.uploader_key += 1

        st.rerun()


# ==================================================
# FILE ORDER SECTION
# ==================================================

if ordered_files:

    st.subheader("2. Arrange File Order")

    st.write(
        "The PDF will be created in the order shown below."
    )


    # ----------------------------------------------
    # SELECT FILE
    # ----------------------------------------------

    file_names = [
        file.name
        for file in ordered_files
    ]


    selected_file_name = st.selectbox(
        "Select a file to move",
        file_names
    )


    selected_index = file_names.index(
        selected_file_name
    )


    # ----------------------------------------------
    # UP / DOWN BUTTONS
    # ----------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "⬆️ Move Up",
            use_container_width=True
        ):

            if selected_index > 0:

                st.session_state.file_order[
                    selected_index
                ], st.session_state.file_order[
                    selected_index - 1
                ] = (
                    st.session_state.file_order[
                        selected_index - 1
                    ],
                    st.session_state.file_order[
                        selected_index
                    ]
                )

                st.rerun()


    with col2:

        if st.button(
            "⬇️ Move Down",
            use_container_width=True
        ):

            if selected_index < len(
                st.session_state.file_order
            ) - 1:

                st.session_state.file_order[
                    selected_index
                ], st.session_state.file_order[
                    selected_index + 1
                ] = (
                    st.session_state.file_order[
                        selected_index + 1
                    ],
                    st.session_state.file_order[
                        selected_index
                    ]
                )

                st.rerun()


    # ----------------------------------------------
    # SHOW CURRENT ORDER
    # ----------------------------------------------

    st.write("### 📋 Current File Order")


    for number, file in enumerate(
        ordered_files,
        start=1
    ):

        st.write(
            f"**{number}.** 📄 {file.name}"
        )


# ==================================================
# VIEW FILES
# ==================================================

if ordered_files:

    st.subheader("3. View Uploaded Files")


    if st.button(
        "👁️ View Files",
        use_container_width=True
    ):

        for number, file in enumerate(
            ordered_files,
            start=1
        ):

            st.write("---")

            st.write(
                f"### {number}. 📄 {file.name}"
            )


            # --------------------------------------
            # IMAGE
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
            # PDF
            # --------------------------------------

            elif file.name.lower().endswith(
                ".pdf"
            ):

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
                        matrix=fitz.Matrix(
                            1.5,
                            1.5
                        )
                    )


                    image_bytes = pix.tobytes(
                        "png"
                    )


                    st.image(
                        image_bytes,
                        caption=(
                            f"{file.name} - "
                            f"Page {page_number + 1}"
                        ),
                        use_container_width=True
                    )


                pdf_document.close()


# ==================================================
# MERGE FILES
# ==================================================

if ordered_files:

    st.subheader("4. Merge PDF / Image Files")


    if st.button(
        "🔄 Merge PDF / Image Files",
        type="primary",
        use_container_width=True
    ):

        try:

            # Create output PDF
            output_path = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ).name


            pdf_writer = PdfWriter()


            # --------------------------------------
            # PROCESS FILES IN SELECTED ORDER
            # --------------------------------------

            for file in ordered_files:

                file_name = file.name.lower()


                # ----------------------------------
                # PDF FILE
                # ----------------------------------

                if file_name.endswith(".pdf"):

                    reader = PdfReader(file)


                    for page in reader.pages:

                        pdf_writer.add_page(page)


                # ----------------------------------
                # IMAGE FILE
                # ----------------------------------

                elif file_name.endswith(
                    (".jpg", ".jpeg", ".png")
                ):

                    image = Image.open(
                        file
                    ).convert("RGB")


                    image_path = (
                        tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".pdf"
                        ).name
                    )


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


            # Save merged PDF
            st.session_state.merged_pdf = (
                output_path
            )


            st.success(
                "✅ Files merged successfully!"
            )


        except Exception as e:

            st.error(
                f"❌ Error: {str(e)}"
            )


# ==================================================
# MERGED PDF
# ==================================================

if st.session_state.merged_pdf:

    st.subheader("5. Merged PDF")


    merged_pdf = (
        st.session_state.merged_pdf
    )


    # ----------------------------------------------
    # VIEW MERGED PDF
    # ----------------------------------------------

    if st.button(
        "👁️ View Merged PDF",
        use_container_width=True
    ):

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
            f"✅ Merged PDF contains "
            f"{len(pdf_document)} page(s)."
        )


        # Show every page

        for page_number in range(
            len(pdf_document)
        ):

            page = pdf_document[
                page_number
            ]


            pix = page.get_pixmap(
                matrix=fitz.Matrix(
                    1.5,
                    1.5
                )
            )


            image_bytes = pix.tobytes(
                "png"
            )


            st.image(
                image_bytes,
                caption=(
                    f"Merged PDF - "
                    f"Page {page_number + 1}"
                ),
                use_container_width=True
            )


        pdf_document.close()


    # ----------------------------------------------
    # DOWNLOAD
    # ----------------------------------------------

    with open(
        merged_pdf,
        "rb"
    ) as pdf_file:

        st.download_button(
            label="⬇️ Download Merged PDF",
            data=pdf_file,
            file_name="merged_files.pdf",
            mime="application/pdf",
            use_container_width=True
        )
