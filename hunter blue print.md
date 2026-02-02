This is the definitive technical and strategic blueprint for **Project Hunter**, reflecting a complete integration of our previous discussions, the Master Plan, and the current operational shift requested by the client.

# **Project Hunter: Comprehensive System Documentation**

## **1\. Executive Vision**

Project Hunter is a high-velocity digital ecosystem designed to exploit the **"Zero Hour"** window—the period between a news event breaking on social media and its saturation on mainstream search engines. The goal is to build an autonomous intelligence pipeline that monitors, analyzes, and eventually replicates the success factors of top-tier Google Discover domains.

## **2\. Client Insights & Strategic Demands**

* **The "Niche-First" Philosophy:** We are not building a brand or buying a domain yet. The client’s current priority is **uncovering the winning niche**. We must prove which sector (Space, Health, Physics, Tech, etc.) has the highest Discover velocity before committing to a brand identity.  
* **Reverse Engineering Success:** The client doesn't want to reinvent the wheel. The system must replicate the DNA of established giants like *Space.com*, *Phys.org*, and *Daily Galaxy*.  
* **Trust in Expertise:** The client has deferred tech stack decisions (LLMs, APIs) to us, prioritizing performance and "Zero Hour" lead time over specific tool preferences.  
* **Aged Domain Preference:** Once the niche is locked, the strategy favors acquiring a clean, aged domain to skip the Google "sandbox" and gain immediate trust for rapid indexing.

## **3\. The "Zero Hour" Technical Architecture**

The system operates as a **Multi-Agent Orchestration (MAO)** model. Every layer is decoupled to allow for real-time adjustments if Google’s algorithms shift.

### **A. The Scout (Ingestion Layer)**

* **Recursive Competitor Discovery:** Starting with the 7 seed URLs provided, the Scout will crawl outbound links and metadata to identify hundreds of secondary competitors.  
* **Triangulated Signal Monitoring:**  
  * **X (via Netrows):** Monitoring high-velocity handles for keyword spikes.  
  * **Reddit API:** Tracking "Rising" posts in niche subreddits (r/science, r/space, etc.).  
  * **RSS Sentinel:** Polling competitor XML feeds every 60 seconds to catch the exact moment of publication.

### **B. The Architect (Analysis Layer)**

* **DNA Extraction:** This agent performs a forensic audit of competitor articles.  
  * **Technical:** HTML structure, Meta-tags, Schema.org (NewsArticle / Article), and PageSpeed metrics.  
  * **Visual:** Image aspect ratios (targeting 1200px WebP) and placement frequency.  
  * **Content:** Word count (800–1200 word target), curiosity-gap title patterns, and subheading density.

### **C. The Intelligence Layer (Logic & Monitoring)**

* **Niche Velocity %:** A proprietary metric calculating which niche currently owns the largest share of the Discover feed at any given hour.  
* **Self-Correction:** If the "Alchemist" (future phase) sees a drop in Discover impressions, the Architect re-audits the top 10 winners to adjust the content criteria.

## **4\. Finalized Tech Stack (Phase 1 & 2 Focus)**

* **The Brains:**  
  * **Primary:** Claude 3.5 Sonnet (via Anthropic API) for technical analysis and agentic coding.  
  * **Secondary/Fallback:** GPT-4o/5.2 (via OpenAI API) for trend scoring and cross-verification.  
* **Agentic Development:** **Claude Code (CLI)** for terminal-based automation, self-healing code, and real-time debugging.  
* **The Pulse (Social APIs):**  
  * **Netrows:** Our primary "Zero Hour" engine for X and social signals ($50/mo Startup plan).  
  * **Reddit API:** Direct monitoring of viral community trends (Developer/Script access).  
* **The Crawler:** Playwright with **Stealth-Plugin** to simulate mobile-first Google Discover environments without triggering CAPTCHAs or bot-detection.  
* **Environment:** Python 3.11+ with FastAPI/Streamlit for the monitoring dashboard.

## **5\. Phase 1 & 2: Execution Roadmap (The Immediate Step-by-Step)**

### **Step 1: Ingestion Setup (Current Focus)**

* Authenticate Claude Code with the provided Anthropic API keys.  
* Configure the **Netrows** and **Reddit** watchers to begin keyword velocity tracking.  
* Start the recursive crawl of the 7 seed URLs to build the "Competitor Master List."

### **Step 2: Niche Discovery Report**

* The system will run 24/7 for a defined period (e.g., 48-72 hours).  
* **Deliverable:** A data-heavy report showing which niche (Space, Health, Physics, Tech) currently dominates Discover and where the "Zero Hour" gap is largest.

### **Step 3: Domain Forensic Audit**

* Once a niche is chosen, we assist the client in finding an **Aged Domain**.  
* We will audit the domain for historical spam, backlink quality, and previous niche alignment.

## **6\. Client Responsibilities & Access Provided**

* **Anthropic Console:** Access granted (Developer/Admin role).  
* **OpenAI Platform:** Access granted.  
* **Netrows:** API credentials provided (Startup Plan).  
* **Seed Competitors:** 7 high-authority sites provided.  
* **Niches:** Space, Astronomy, Health, Physics, Technology confirmed.

---

