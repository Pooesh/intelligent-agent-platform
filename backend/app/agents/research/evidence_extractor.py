
import json
import re
from urllib.parse import urlsplit, urlunsplit

from app.llm.llm_service import LLMService


class EvidenceExtractor:

    def __init__(self):
        self.llm_service = LLMService()

    @staticmethod
    def _normalize_url(url: str) -> str | None:
        """Normalize URLs for reliable source matching."""

        if not isinstance(url, str) or not url.strip():
            return None

        try:
            parsed = urlsplit(url.strip())
            hostname = parsed.hostname

            if not hostname:
                return None

            if parsed.scheme.lower() not in ("http", "https"):
                return None

            hostname = hostname.lower()
            port = parsed.port

            if port and port not in (80, 443):
                hostname = f"{hostname}:{port}"

            path = re.sub(r"/{2,}", "/", parsed.path)
            path = path.rstrip("/") or "/"

            return urlunsplit((
                "https",
                hostname,
                path,
                "",
                ""
            ))

        except ValueError:
            return None

    @staticmethod
    def _parse_json_response(raw_response: str):
        """Parse JSON objects, arrays, and Markdown-wrapped JSON."""

        if not isinstance(raw_response, str):
            print("JSON parsing error: response is not a string.")
            return None

        cleaned = raw_response.strip()

        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            cleaned,
            flags=re.IGNORECASE
        ).strip()

        try:
            parsed = json.loads(cleaned)

            if isinstance(parsed, (dict, list)):
                return parsed

            print("JSON parsing error: unsupported JSON structure.")
            return None

        except json.JSONDecodeError as error:
            print(f"JSON parsing error: {error}")
            return None

    @staticmethod
    def _clean_documentation_content(content: str) -> str:
        """Remove obvious navigation and footer noise."""

        if not isinstance(content, str) or not content.strip():
            return ""

        cleaned_lines = []

        navigation_patterns = [
            r"^github$",
            r"^discord$",
            r"^twitter$",
            r"^linkedin$",
            r"^youtube$",
            r"^home$",
            r"^menu$",
            r"^search$",
            r"^navigation$",
            r"^table of contents$",
            r"^on this page$",
            r"^edit this page$",
            r"^previous$",
            r"^next$",
            r"^back to top$",
            r"^was this page helpful\??$",
            r"^privacy policy$",
            r"^terms of service$",
            r"^cookie policy$",
        ]

        for line in content.splitlines():

            stripped = line.strip()

            if not stripped:
                continue

            normalized = re.sub(
                r"^[#>*\-\s]+|[#>*\-\s]+$",
                "",
                stripped
            ).strip().lower()

            if not normalized:
                continue

            if any(
                re.match(pattern, normalized)
                for pattern in navigation_patterns
            ):
                continue

            if len(normalized) <= 35 and normalized in {
                "documentation",
                "api reference",
                "community",
                "resources",
                "quick links",
                "feedback",
                "contact",
                "copyright",
            }:
                continue

            cleaned_lines.append(stripped)

        return "\n".join(cleaned_lines)

    def _split_sentences(self, content: str) -> list[str]:
        """Clean and split documentation content into sentences."""

        cleaned_content = self._clean_documentation_content(content)

        if not cleaned_content:
            return []

        sentences = re.split(
            r"(?<=[.!?])\s+",
            cleaned_content.strip()
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def validate_evidence(
        self,
        evidence: list[dict],
        search_results: list[dict]
    ) -> list[dict]:
        """Validate evidence against original documentation and framework."""

        validated = []
        source_map = {}

        for result in search_results:

            if not isinstance(result, dict):
                continue

            normalized_url = self._normalize_url(
                result.get("url", "")
            )

            if normalized_url:
                source_map[normalized_url] = result

        required_fields = [
            "framework",
            "feature",
            "description",
            "source_title",
            "source_url",
            "supporting_evidence",
        ]

        for item in evidence:

            if not isinstance(item, dict):
                continue

            if not all(
                isinstance(item.get(field), str)
                and item[field].strip()
                for field in required_fields
            ):
                print("Rejected evidence: missing required fields.")
                continue

            normalized_url = self._normalize_url(
                item["source_url"]
            )

            if not normalized_url:
                print(
                    "Rejected invalid source URL:",
                    item["source_url"]
                )
                continue

            original_source = source_map.get(normalized_url)

            if not original_source:
                print(
                    "Rejected unknown source URL:",
                    item["source_url"]
                )
                continue

            expected_framework = original_source.get("framework")

            if (
                expected_framework
                and item["framework"].strip().lower()
                != expected_framework.strip().lower()
            ):
                print(
                    "Rejected framework mismatch:",
                    item["framework"],
                    "!=",
                    expected_framework
                )
                continue

            original_content = original_source.get("content", "")

            if not isinstance(original_content, str):
                continue

            normalized_content = " ".join(
                original_content.lower().split()
            )

            normalized_evidence = " ".join(
                item["supporting_evidence"].lower().split()
            )

            if normalized_evidence not in normalized_content:
                print("\n========== EVIDENCE DEBUG ==========")
                print("Framework:", item["framework"])
                print("Feature:", item["feature"])
                print("Source URL:", item["source_url"])
                print("Supporting evidence:")
                print(repr(item["supporting_evidence"]))
                print("Original content:")
                print(repr(original_content[:3000]))
                print("====================================\n")
                continue

            validated_item = item.copy()

            validated_item["architecture"] = (
                "Not independently verified"
            )

            validated.append(validated_item)

        unique_evidence = []
        seen = set()

        for item in validated:

            duplicate_key = (
                item["framework"].strip().lower(),
                item["feature"].strip().lower(),
                self._normalize_url(item["source_url"]),
                item["supporting_evidence"].strip().lower(),
            )

            if duplicate_key in seen:
                continue

            seen.add(duplicate_key)
            unique_evidence.append(item)

        return unique_evidence

    async def verify_semantic_support(
        self,
        evidence: list[dict]
    ) -> list[dict]:
        """Verify each evidence item independently against its source sentence."""

        if not evidence:
            return []

        verified_evidence = []

        print(
            "\nStarting independent semantic evidence verification..."
        )

        for index, item in enumerate(evidence):

            verification_item = {
                "evidence_id": index,
                "framework": item["framework"],
                "feature": item["feature"],
                "claim": item["description"],
                "source_sentence": item["supporting_evidence"]
            }

            prompt = f"""
You are a strict technical fact-checker.

Compare the claim with its source sentence.

Use ONLY the supplied source sentence.

Rules:
1. Mark "supported" only when the entire claim is explicitly established.
2. Mark "partially_supported" when only part of the claim is established.
3. Mark "unsupported" when the source does not establish the claim.
4. Do not use external knowledge.
5. Do not infer missing technical details.
6. Do not assume that related information proves the claim.
7. Evaluate only this one evidence item.

Return ONLY valid JSON in this exact structure:

{{
    "evidence_id": {index},
    "status": "supported",
    "reason": "Short explanation based only on the source."
}}

Allowed statuses:
- supported
- partially_supported
- unsupported

Evidence:
{json.dumps(verification_item, ensure_ascii=False, indent=2)}
"""

            try:
                response = await self.llm_service.generate_response(
                    message=prompt,
                    provider="ollama",
                )

                print(
                    f"\nVerification response for evidence {index}:"
                )
                print(repr(response))

                parsed = self._parse_json_response(response)

                if not isinstance(parsed, dict):
                    print(
                        f"Rejected evidence {index}: invalid JSON."
                    )
                    continue

                evidence_id = parsed.get("evidence_id")
                status = parsed.get("status")
                reason = parsed.get("reason")

                if (
                    not isinstance(evidence_id, int)
                    or isinstance(evidence_id, bool)
                    or evidence_id != index
                ):
                    print(
                        f"Rejected evidence {index}: "
                        "incorrect evidence ID."
                    )
                    continue

                if status not in (
                    "supported",
                    "partially_supported",
                    "unsupported"
                ):
                    print(
                        f"Rejected evidence {index}: invalid status."
                    )
                    continue

                if not isinstance(reason, str) or not reason.strip():
                    print(
                        f"Rejected evidence {index}: missing reason."
                    )
                    continue

                if status != "supported":
                    print(
                        f"Rejected {item['framework']}: "
                        f"{item['feature']} ({status}) - {reason}"
                    )
                    continue

                verified_item = item.copy()
                verified_item["verification_status"] = status
                verified_item["verification_reason"] = reason.strip()

                verified_evidence.append(verified_item)

                print(
                    f"Verified {item['framework']}: "
                    f"{item['feature']}"
                )

            except Exception as exc:
                print(
                    f"Verification failed for evidence {index}: {exc}"
                )
                continue

        print(
            "\n========== SEMANTIC VERIFICATION SUMMARY =========="
        )
        print("Original evidence:", len(evidence))
        print("Supported evidence:", len(verified_evidence))
        print(
            "Rejected evidence:",
            len(evidence) - len(verified_evidence)
        )
        print("===================================================\n")

        return verified_evidence

    async def _extract_framework(
        self,
        framework: str,
        framework_results: list[dict]
    ) -> list[dict]:
        """Extract evidence using LLM-selected sentence IDs."""

        if not framework_results:
            print(f"No sources available for {framework}.")
            return []

        evidence_items = []
        source_lookup = {}

        # Step 1: Prepare source records and numbered sentences.
        for result in framework_results:

            original_url = result.get("url", "")
            normalized_url = self._normalize_url(original_url)

            if not normalized_url:
                continue

            if normalized_url in source_lookup:
                continue

            original_content = result.get("content", "")

            if not isinstance(original_content, str):
                continue

            content = original_content[:2500]
            sentences = self._split_sentences(content)

            if not sentences:
                continue

            source_index = len(evidence_items)

            source_lookup[normalized_url] = result

            evidence_items.append({
                "source_index": source_index,
                "title": result.get("title", ""),
                "url": original_url,
                "normalized_url": normalized_url,
                "sentences": [
                    {
                        "sentence_id": index,
                        "text": sentence
                    }
                    for index, sentence in enumerate(sentences)
                ]
            })

        if not evidence_items:
            print(f"No usable sentences for {framework}.")
            return []

        # Step 2: Prepare candidate sentences for the LLM.
        candidate_sentences = []

        for source_item in evidence_items:

            for sentence_item in source_item["sentences"]:

                candidate_sentences.append({
                    "source_index": source_item["source_index"],
                    "sentence_id": sentence_item["sentence_id"],
                    "text": sentence_item["text"]
                })

        # NEW: Diagnostic logging of the exact candidate IDs.
        print(
            f"\n========== {framework} CANDIDATE SENTENCES =========="
        )

        for source_item in evidence_items:

            print(
                f"\nSource index: {source_item['source_index']}"
            )
            print(
                f"Source title: {source_item['title']}"
            )
            print(
                "Available sentence IDs:",
                [
                    sentence["sentence_id"]
                    for sentence in source_item["sentences"]
                ]
            )

            for sentence in source_item["sentences"]:
                print(
                    f"  ID {sentence['sentence_id']}: "
                    f"{sentence['text'][:200]}"
                )

        print("====================================================\n")

        prompt = f"""
You are a technical documentation evidence selector.

Framework: {framework}

Your task is to identify useful technical facts from the supplied
documentation sentences.

STRICT RULES:

1. Use ONLY the supplied candidate sentences.
2. Select a sentence only if it contains a meaningful technical fact.
3. Do not invent facts, features, or technical details.
4. Do not rewrite or reproduce the sentence text in your response.
5. Do not create source indexes or sentence IDs.
6. Use the exact source_index and sentence_id of the selected candidate.
7. Provide a short feature label describing the topic of the sentence.
8. Do not use a feature label to introduce facts not present in the sentence.
9. Avoid navigation text, headings, menus, and unrelated content.
10. Select distinct useful evidence when available.
11. If no useful evidence exists, return an empty evidence array.
12. Return valid JSON only, without Markdown fences or explanations.

Output requirements:

Return a JSON object with an "evidence" array.

Each entry in the array must contain:
- source_index: an integer identifying the candidate's source.
- sentence_id: an integer identifying the sentence within that source.
- feature: a short descriptive feature label.

Do not include URLs, descriptions, architecture details, or supporting
quotes in your response. Python will reconstruct those values from
the original documentation.

Candidate sentences:

{json.dumps(candidate_sentences, ensure_ascii=False, indent=2)}
"""

        # Step 3: Ask the LLM to select candidate sentences.
        print(f"\nExtracting evidence for {framework}...")

        try:
            response = await self.llm_service.generate_response(
                message=prompt,
                provider="ollama",
            )
        except Exception as exc:
            print(f"LLM extraction failed for {framework}: {exc}")
            return []

        print(
            f"\n========== {framework} RAW RESPONSE =========="
        )
        print(repr(response))
        print("===============================================\n")

        parsed_response = self._parse_json_response(response)

        # Accept both {"evidence": [...]} and direct [...]
        if isinstance(parsed_response, dict):
            extracted_items = parsed_response.get("evidence")
        elif isinstance(parsed_response, list):
            extracted_items = parsed_response
        else:
            extracted_items = None

        if not isinstance(extracted_items, list):
            print(f"Invalid evidence list for {framework}.")
            return []

        # Step 4: Reconstruct evidence using trusted Python-side data.
        reconstructed_evidence = []
        seen = set()

        for item in extracted_items:

            if not isinstance(item, dict):
                continue

            source_index = item.get("source_index")
            sentence_id = item.get("sentence_id")
            feature = item.get("feature")

            if (
                not isinstance(source_index, int)
                or isinstance(source_index, bool)
                or not isinstance(sentence_id, int)
                or isinstance(sentence_id, bool)
            ):
                print(
                    f"Rejected invalid IDs for {framework}:",
                    source_index,
                    sentence_id
                )
                continue

            if not isinstance(feature, str):
                print(f"Rejected invalid feature label for {framework}.")
                continue

            feature = feature.strip()

            if not feature or feature.lower() in {
                "...",
                "feature",
                "feature name",
                "label",
            }:
                print(
                    f"Rejected empty or placeholder feature for {framework}."
                )
                continue

            if source_index < 0 or source_index >= len(evidence_items):
                print(
                    f"Rejected invalid source index for {framework}:",
                    source_index
                )
                continue

            source_item = evidence_items[source_index]
            sentences = source_item["sentences"]

            if sentence_id < 0 or sentence_id >= len(sentences):
                print(
                    f"Rejected invalid sentence ID for {framework}:",
                    sentence_id
                )
                continue

            normalized_url = source_item["normalized_url"]
            original_source = source_lookup.get(normalized_url)

            if original_source is None:
                continue

            original_sentence = sentences[sentence_id]["text"]

            duplicate_key = (
                normalized_url,
                sentence_id,
                feature.lower()
            )

            if duplicate_key in seen:
                continue

            seen.add(duplicate_key)

            reconstructed_evidence.append({
                "framework": framework,
                "feature": feature,
                "description": original_sentence,
                "architecture": "Not independently verified",
                "source_title": source_item["title"] or "Untitled source",
                "source_url": original_source.get("url", ""),
                "supporting_evidence": original_sentence,
            })

        # Step 5: Validate reconstructed evidence against original sources.
        validated_evidence = self.validate_evidence(
            reconstructed_evidence,
            framework_results
        )

        print(f"{framework} selected: {len(extracted_items)}")
        print(
            f"{framework} reconstructed: "
            f"{len(reconstructed_evidence)}"
        )
        print(
            f"{framework} validated: "
            f"{len(validated_evidence)}"
        )

        return validated_evidence

    async def extract(
        self,
        search_results: list[dict]
    ) -> list[dict]:
        """Extract and validate evidence independently for each framework."""

        if not search_results:
            return []

        frameworks = [
            "LangGraph",
            "CrewAI",
            "AutoGen",
        ]

        all_validated_evidence = []

        # Step 1: Group search results by framework.
        framework_groups = {
            framework: []
            for framework in frameworks
        }

        for result in search_results:

            if not isinstance(result, dict):
                continue

            framework = result.get("framework")

            if framework in framework_groups:
                framework_groups[framework].append(result)

        # Step 2: Extract evidence independently for each framework.
        for framework in frameworks:

            framework_results = framework_groups[framework]

            print(
                f"\n{framework}: "
                f"{len(framework_results)} source(s)"
            )

            validated = await self._extract_framework(
                framework,
                framework_results
            )

            all_validated_evidence.extend(validated)

        # Step 3: Final validation and deduplication.
        final_evidence = self.validate_evidence(
            all_validated_evidence,
            search_results
        )

        print("\nExact evidence validation completed.")
        print("Validated evidence:", len(final_evidence))

        # Step 4: Mark the actual verification method.
        for item in final_evidence:
            item["verification_status"] = "exact_match"
            item["verification_method"] = "deterministic"

        # Step 5: Final summary.
        print("\n========== FINAL EVIDENCE SUMMARY ==========")

        for framework in frameworks:

            count = sum(
                1
                for item in final_evidence
                if item["framework"] == framework
            )

            print(
                f"{framework}: "
                f"{count} validated evidence item(s)"
            )

        print(
            "Total validated evidence:",
            len(final_evidence)
        )

        print("============================================\n")

        return final_evidence
