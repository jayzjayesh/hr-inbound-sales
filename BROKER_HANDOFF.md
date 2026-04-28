# Acme Logistics: AI Inbound Carrier Agent — Build & Handoff Document

**To:** Acme Logistics Leadership Team
**From:** Jayesh (AI Engineering Partner)
**Date:** April 28, 2026
**Subject:** Build Description & Handoff for Inbound Carrier Sales Agent

---

## 1. Executive Summary

We are thrilled to hand over the **AI Inbound Carrier Sales Agent**, a voice-native AI solution custom-built for Acme Logistics on the HappyRobot platform. This system is designed to automate the entire lifecycle of an inbound carrier call—from initial greeting and compliance verification to load matching, rate negotiation, and final handoff. 

By handling routine inbound inquiries, verifying authority in real-time, and negotiating within strict margins, this AI agent frees up Acme's human brokers to focus on relationship building, exception management, and high-value outbound sales.

## 2. Core Capabilities

Your new AI agent operates with the expertise of a seasoned freight broker. It is equipped with the following core features:

### A. Real-Time FMCSA Compliance Verification
Before discussing any freight, the agent asks for the caller's MC (Motor Carrier) number. It instantly queries the live FMCSA database via our custom-built integration backend to verify:
- Operating Authority Status (Authorized vs. Not Authorized)
- Safety Rating
- OOS (Out of Service) status
*If a carrier is not authorized, the agent politely ends the transaction, protecting Acme from compliance risks.*

### B. Intelligent Load Matching
Once verified, the agent asks the carrier for their current location, desired destination, and equipment type (Van, Reefer, Flatbed). It queries Acme's active load board (via our backend API) using fuzzy-matching to find the best available loads and pitches them naturally to the carrier, including critical details like commodities, weight, and pick/drop windows.

### C. Margin-Protected AI Negotiation
The agent is programmed with a sophisticated 3-round negotiation logic:
- It starts by pitching the listed loadboard rate.
- If the carrier counters, it assesses the offer against a hardcoded **90% negotiation floor** (i.e., it will never accept an offer below 90% of the listed rate).
- It counters logically over a maximum of 3 rounds, attempting to save margin (e.g., countering at 95%, then 92%) while maintaining a professional and friendly tone.
- The negotiation floor and logic are entirely hidden from the carrier.

### D. Seamless Handoff
Once a rate is agreed upon, the agent confirms the details (Load ID, Lane, Rate, MC Number) and transfers the call to Acme's live sales team to finalize the digital paperwork and dispatch processes.

## 3. Real-Time Analytics Dashboard

To give Acme Logistics full visibility into the AI's performance, we developed a stunning, real-time analytics dashboard accessible from any web browser.

**Dashboard Features:**
- **Live KPIs:** Monitor Total Calls, Success Rate, Average Revenue per Booked Call, and Average Negotiation Savings (margin protected).
- **Outcome Tracking:** See exactly why calls didn't convert (e.g., "Rate too high", "Carrier not eligible", "No loads available").
- **Carrier Sentiment:** AI-driven analysis of whether carriers were Positive, Neutral, or Negative during the call.
- **Negotiation Performance:** Visual charts comparing the starting loadboard rates versus the final agreed rates to track margin retention.
- **Call Ledger:** A complete, searchable table of recent calls including duration, rounds of negotiation, and final outcomes.

## 4. ROI & Business Value

Deploying this AI agent delivers immediate value to Acme Logistics:
1. **Zero Wait Times:** Carriers never go to voicemail. The agent answers instantly, 24/7.
2. **Margin Protection:** By strictly adhering to the negotiation floor and systematically trying to book freight close to the listed rate, the agent maximizes revenue per load.
3. **Operational Efficiency:** Human brokers save an average of 3–5 minutes per call on carriers who either aren't compliant or want rates above market. They only speak to carriers ready to book.
4. **Compliance Security:** Automated FMCSA checks eliminate the risk of human error when vetting unknown inbound callers.

## 5. Technical Architecture

The solution is robust, scalable, and secure:
- **Voice Agent:** Hosted on the HappyRobot platform, utilizing advanced LLMs and low-latency speech-to-text/text-to-speech models.
- **Backend Infrastructure:** A containerized Python (FastAPI) backend deployed on Render.
- **Security:** All API communication between the AI agent and the backend is secured via hardened `X-API-Key` headers.
- **Extensibility:** The API endpoints are designed to easily plug into Acme's existing TMS (Transportation Management System) in the future.

## 6. Next Steps & Roadmap

The current build operates on an in-memory database of active loads. To bring this to full production parity, we recommend the following Phase 2 implementations:
- **TMS Integration:** Replace the sample load database with a direct API connection to Acme's TMS (e.g., McLeod, MercuryGate) for live read/write of freight availability.
- **Automated Rate Confirmations:** Trigger an email/SMS containing the rate confirmation document automatically upon a successful verbal agreement.
- **Advanced Routing:** Implement rules to transfer calls to specific broker extensions based on the lane or carrier profile.

We are excited to see Acme Logistics scale its operations with this intelligent automation. Please let us know when you are ready to review the live dashboard and conduct test calls.
