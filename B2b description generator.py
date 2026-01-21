import streamlit as st
import pandas as pd
import json
import re
from anthropic import Anthropic

st.set_page_config(page_title="B2B Product Description Generator", layout="wide")

st.title("B2B Jewelry Product Description Generator")
st.markdown("Generate industry-focused, technical product descriptions optimized for wholesale buyers")

# Initialize Anthropic client
client = Anthropic()

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    description_style = st.selectbox(
        "Description Style",
        ["Technical Specifications", "Buyer-Focused", "Manufacturing Details", "Balanced"]
    )
    
    include_sections = st.multiselect(
        "Include Sections",
        ["Specifications", "Materials & Construction", "Pricing Details", "Minimum Order Info", "Care & Handling"],
        default=["Specifications", "Materials & Construction"]
    )
    
    word_count = st.slider("Approximate Word Count", 50, 300, 150)
    
    st.markdown("---")
    st.markdown("### Upload Options")
    upload_type = st.radio("Data Source", ["Shopify CSV Export", "Manual Entry"])

# Main content area
if upload_type == "Shopify CSV Export":
    uploaded_file = st.file_uploader("Upload Shopify Products CSV", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(df)} products")
            
            # Show available products
            if 'Title' in df.columns:
                product_titles = df['Title'].unique().tolist()
                selected_product = st.selectbox("Select Product", product_titles)
                
                # Filter to selected product
                product_data = df[df['Title'] == selected_product].iloc[0]
                
                # Display current product info
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Current Product Information")
                    
                    # Extract key fields
                    display_fields = ['Title', 'Vendor', 'Type', 'Tags', 'Variant Price', 
                                    'Variant SKU', 'Variant Grams', 'Body (HTML)']
                    
                    for field in display_fields:
                        if field in product_data and pd.notna(product_data[field]):
                            st.text_input(field, value=str(product_data[field]), disabled=True)
                
                with col2:
                    st.subheader("Product Images")
                    if 'Image Src' in df.columns:
                        images = df[df['Title'] == selected_product]['Image Src'].dropna().unique()
                        for idx, img_url in enumerate(images[:3]):  # Show up to 3 images
                            st.image(img_url, width=200)
                
                # Additional details input
                st.markdown("---")
                st.subheader("Additional Details (Optional)")
                
                col3, col4 = st.columns(2)
                with col3:
                    metal_purity = st.text_input("Metal Purity (e.g., 14K, 18K, .925)", "")
                    stone_details = st.text_input("Stone Details (e.g., CZ, Diamond, dimensions)", "")
                    chain_length = st.text_input("Chain Length/Dimensions", "")
                
                with col4:
                    finish = st.text_input("Finish (e.g., Polished, Brushed, Rhodium)", "")
                    clasp_type = st.text_input("Clasp/Closure Type", "")
                    moq = st.text_input("Minimum Order Quantity", "")
                
                # Generate button
                if st.button("Generate B2B Description", type="primary"):
                    with st.spinner("Generating professional description..."):
                        
                        # Prepare context for Claude
                        context = f"""
Product Title: {product_data.get('Title', 'N/A')}
Vendor: {product_data.get('Vendor', 'N/A')}
Type: {product_data.get('Type', 'N/A')}
SKU: {product_data.get('Variant SKU', 'N/A')}
Price: ${product_data.get('Variant Price', 'N/A')}
Weight: {product_data.get('Variant Grams', 'N/A')}g
Tags: {product_data.get('Tags', 'N/A')}
Current Description: {product_data.get('Body (HTML)', 'N/A')}

Additional Details:
Metal Purity: {metal_purity if metal_purity else 'Not specified'}
Stone Details: {stone_details if stone_details else 'Not specified'}
Dimensions: {chain_length if chain_length else 'Not specified'}
Finish: {finish if finish else 'Not specified'}
Clasp Type: {clasp_type if clasp_type else 'Not specified'}
MOQ: {moq if moq else 'Not specified'}
"""
                        
                        prompt = f"""You are a professional B2B product description writer for the wholesale jewelry industry. 

Create a {description_style.lower()} product description for wholesale buyers that is:
- Industry-focused and technical (no marketing fluff)
- Approximately {word_count} words
- Structured for B2B decision-making
- Focused on specifications, materials, and value proposition

Include these sections: {', '.join(include_sections)}

Product Information:
{context}

Write a professional description that a jewelry buyer or procurement manager would find useful for making purchasing decisions. Focus on facts, specifications, and business-relevant details."""

                        # Call Claude API
                        try:
                            message = client.messages.create(
                                model="claude-sonnet-4-20250514",
                                max_tokens=1000,
                                messages=[
                                    {"role": "user", "content": prompt}
                                ]
                            )
                            
                            generated_description = message.content[0].text
                            
                            st.markdown("---")
                            st.subheader("Generated B2B Description")
                            st.markdown(generated_description)
                            
                            # Download options
                            col5, col6 = st.columns(2)
                            with col5:
                                st.download_button(
                                    "Download as TXT",
                                    generated_description,
                                    file_name=f"{product_data.get('Variant SKU', 'product')}_description.txt",
                                    mime="text/plain"
                                )
                            
                            with col6:
                                # Create HTML version
                                html_description = generated_description.replace('\n\n', '</p><p>').replace('\n', '<br>')
                                html_description = f"<p>{html_description}</p>"
                                
                                st.download_button(
                                    "Download as HTML",
                                    html_description,
                                    file_name=f"{product_data.get('Variant SKU', 'product')}_description.html",
                                    mime="text/html"
                                )
                            
                        except Exception as e:
                            st.error(f"Error generating description: {str(e)}")
                            st.info("Note: This tool requires an Anthropic API key to be configured.")
            
        except Exception as e:
            st.error(f"Error loading CSV: {str(e)}")

else:  # Manual Entry
    st.subheader("Manual Product Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Product Title*", "")
        sku = st.text_input("SKU", "")
        product_type = st.text_input("Product Type (e.g., Ring, Necklace, Bracelet)", "")
        vendor = st.text_input("Vendor/Manufacturer", "")
        price = st.number_input("Wholesale Price ($)", min_value=0.0, step=0.01)
    
    with col2:
        metal_purity = st.text_input("Metal Purity", "")
        stone_details = st.text_area("Stone/Gemstone Details", "")
        dimensions = st.text_input("Dimensions/Size", "")
        weight = st.number_input("Weight (grams)", min_value=0.0, step=0.01)
        finish = st.text_input("Finish", "")
    
    additional_notes = st.text_area("Additional Technical Details", "")
    
    if st.button("Generate Description", type="primary"):
        if not title:
            st.error("Product Title is required")
        else:
            with st.spinner("Generating description..."):
                context = f"""
Product Title: {title}
SKU: {sku}
Type: {product_type}
Vendor: {vendor}
Price: ${price}
Metal Purity: {metal_purity}
Stone Details: {stone_details}
Dimensions: {dimensions}
Weight: {weight}g
Finish: {finish}
Additional Notes: {additional_notes}
"""
                
                prompt = f"""You are a professional B2B product description writer for the wholesale jewelry industry. 

Create a {description_style.lower()} product description for wholesale buyers that is:
- Industry-focused and technical (no marketing fluff)
- Approximately {word_count} words
- Structured for B2B decision-making
- Focused on specifications, materials, and value proposition

Include these sections: {', '.join(include_sections)}

Product Information:
{context}

Write a professional description that a jewelry buyer or procurement manager would find useful for making purchasing decisions. Focus on facts, specifications, and business-relevant details."""

                try:
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1000,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    generated_description = message.content[0].text
                    
                    st.markdown("---")
                    st.subheader("Generated B2B Description")
                    st.markdown(generated_description)
                    
                    st.download_button(
                        "Download Description",
                        generated_description,
                        file_name=f"{sku if sku else 'product'}_description.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating description: {str(e)}")
                    st.info("Note: This tool requires an Anthropic API key to be configured.")

# Footer
st.markdown("---")
st.markdown("""
### Tips for Best Results
- Upload complete Shopify product data with all relevant fields
- Add specific technical details (metal purity, stone specs, dimensions)
- Choose the appropriate style for your target buyers
- Review and edit generated descriptions before using in your catalog
""")
