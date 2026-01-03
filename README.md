# Horizon

Monitor a live Certificate Transparency Stream for domain squatting attempts to detect phishing/impersonation of your domain assets.

Squatting/Impersonation of Domains by malicious third parties might trick users of the official domain and lead to phishing and credential theft.

---

Horizon operates on a best-effort model with the goal to give insight into the frequency of such attempts against popular domains and help anybody detect domain squatting attemtps

Currently the following domain squatting techniques can be detected:

- ComboSquatting     : An Attacker registers a domain name that contains the SLD of the offical domain but adds a hyphen and a word before or after. Example: amazon-login.com, free-amazon.com
- TLDSquatting       : An Attacker registers a domain name that has the same SLD as the offical domain but registers it with a different TLD. Example: amazon.monster, amazon.tatoo, amazon.dev 
- Typosquatting      : An Attacker registers a domain name that users might accidentally type into the URL bar or mistake as the official domain at first glance. Example: amazom.com, amazo.com
- SubdomainSquatting : An Attacker registers an arbitiary domain name and adds the offical SLD as a subdomain. Example: amazon.securelogin.com, amazon.marketplace.com

---

Unilke other tools, Horizon doesn't pre-generate Permutations for the domain names that should be monitored. Instead the tool uses 4 Detection functions to check the live streamed Certificate Transparency data for the squatting methods.
As with many Security tool, the risk for false positives is high. This is especially true for TypoSquatting-detection as it uses the Damerau-Levenshtein-Distance which only keeps track of edits needed to transform string1 into string2, omitting context.

