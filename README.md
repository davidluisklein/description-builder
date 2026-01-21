# B2B Jewelry Product Description Generator

Generate professional, technical product descriptions for wholesale jewelry buyers using AI.

## Features
- Import products from Shopify CSV exports
- Manual product entry
- Customizable description styles
- Multiple output formats (TXT, HTML)

## Setup

1. Clone the repository:
```bash
   git clone https://github.com/yourusername/jewelry-description-generator.git
   cd jewelry-description-generator
```

2. Install dependencies:
```bash
   pip install -r requirements.txt
```

3. Set up your Anthropic API key:
   
   **Option A: Environment Variable**
```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
```
   
   **Option B: Streamlit Secrets (Recommended)**
   Create `.streamlit/secrets.toml`:
```toml
   ANTHROPIC_API_KEY = "your-api-key-here"
```

4. Run the app:
```bash
   streamlit run app.py
```

## Usage

1. Choose between Shopify CSV upload or manual entry
2. Configure description style and sections in the sidebar
3. Fill in product details
4. Click "Generate B2B Description"
5. Download in your preferred format

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `ANTHROPIC_API_KEY` in Secrets settings

## License
MIT
