# Universal Integration Protocol Licensing Strategy

## Overview

The Universal Integration Protocol (UIP) uses a dual licensing model to balance open-source community development with commercial sustainability. This document explains our licensing approach and the rationale behind it.

## Dual Licensing Model

UIP is available under two licensing options:

1. **GNU Affero General Public License v3.0 (AGPL-3.0)** for non-commercial use
2. **Commercial License** for commercial applications

### AGPL-3.0 License

The AGPL-3.0 license is a strong copyleft license that:

- Allows free use, modification, and distribution
- Requires derivative works to be licensed under AGPL-3.0
- Importantly, extends the distribution requirement to network use (closing the "SaaS loophole")
- Requires source code to be provided to users who interact with the software over a network

This license is ideal for:
- Individual developers
- Educational institutions
- Non-profit organizations
- Open-source projects
- Research and development

### Commercial License

Our commercial license removes certain restrictions of the AGPL-3.0 license and provides additional benefits:

- Permission to use in commercial products without AGPL-3.0 obligations
- Ability to create proprietary/closed-source modifications
- No requirement to share source code modifications
- Technical support and maintenance options
- Legal indemnification

This license is required for:
- SaaS providers using UIP in their applications
- Companies integrating UIP into commercial products
- Organizations using UIP as part of a paid service
- Any for-profit usage beyond development and evaluation

## Rationale for Dual Licensing

We've chosen this approach to:

1. **Protect Innovation**: Prevent companies from taking the project's code, creating a proprietary version, and competing against the project itself
2. **Empower Small Developers**: Allow individuals and small teams to use the technology freely
3. **Create Sustainable Development**: Generate revenue to fund ongoing development, maintenance, and innovation
4. **Maintain Open Source Ethos**: Keep the core technology open-source and accessible
5. **Prevent Exploitation**: Ensure large corporations can't exploit the project without contributing back financially

## How This Benefits Everyone

### For Individual Developers

- Free access to the full UIP technology stack
- Ability to contribute and shape the project's direction
- Legal clarity around usage rights
- Protection from having their contributions commercialized without compensation

### For Commercial Users

- Access to enterprise features and support
- Legal certainty for commercial applications
- Indemnification against legal claims
- Customization options and priority bug fixes
- Supporting ongoing development of the tools they rely on

### For the Project

- Sustainable funding model for long-term development
- Protection against unfair commercial exploitation
- Ability to invest in documentation, tooling, and community support
- Resources to expand language support and features

## Contributor License Agreement (CLA)

To support our dual licensing model, we require all contributors to sign a Contributor License Agreement (CLA). The CLA ensures we have the necessary rights to:

1. Include contributions in the project under both AGPL-3.0 and commercial licenses
2. Maintain licensing flexibility as the project evolves
3. Protect all contributors from legal issues

The CLA does not take away contributors' rights to their code but simply grants us permission to use their contributions according to our licensing model.

## Comparison to Other Licensing Models

### Why Not MIT or Apache 2.0?

While MIT and Apache 2.0 are permissive licenses that promote widespread adoption, they would allow large companies to use UIP in commercial products without contributing back financially. This could undermine our ability to sustain development and would benefit large corporations at the expense of individual developers.

### Why Not GPL-3.0?

The standard GPL-3.0 includes the "network use is not conveying" clause, which creates a loophole for SaaS providers. They can modify the code and use it to provide services without sharing their modifications. AGPL-3.0 closes this loophole.

### Why Not Open Core?

While we do follow some open-core principles, a pure open-core model (where core features are open-source but premium features are proprietary) would fragment the codebase and potentially create conflicts of interest in feature development.

## Commercial Licensing Details

Commercial licenses are customized based on:

1. **Organization size**: Special rates for small businesses and startups
2. **Usage type**: Different terms for direct product integration vs. internal tooling
3. **Support needs**: Various tiers of technical support and services
4. **Deployment scope**: Pricing based on scale of deployment

For commercial licensing inquiries, please contact licensing@universalintegrationprotocol.org

## Future License Evolution

As the project evolves, we may adjust our licensing strategy to better serve the community and ensure sustainability. Any changes will:

1. Respect existing licensees' rights
2. Be transparently communicated well in advance
3. Include transition periods and grandfathering where appropriate
4. Be made with community input

## Frequently Asked Questions

### Can I use UIP in my personal projects?

Yes, you can use UIP freely under the AGPL-3.0 license for personal, non-commercial projects.

### Do I need a commercial license for my startup?

If you're using UIP to provide a service to customers or as part of a commercial product, you'll need a commercial license. We offer startup-friendly pricing to make this accessible.

### What constitutes "commercial use"?

Any use where the primary purpose is to generate revenue or provide paid services. This includes:
- SaaS applications that customers pay to use
- Commercial software products that include UIP
- Consulting services that include UIP implementation
- Enterprise internal tools that directly support revenue-generating activities

### How is the license enforced?

We believe in constructive relationships rather than aggressive enforcement. We'll work with organizations to ensure proper licensing, with legal enforcement as a last resort for willful infringement.

### Can I contribute if I work for a company?

Yes, but you'll need to sign the CLA. If you're contributing on behalf of your company, your company may need to sign a corporate CLA.

### How do I know if my contribution will be used in the commercial version?

Generally, all contributions to the main repository will be available in both the AGPL and commercial versions. The CLA makes this explicit and ensures we have the right to include your code in both versions.

---

This licensing strategy aims to create a balance that protects innovation, rewards creators, and maintains the spirit of open-source collaboration while ensuring long-term sustainability.