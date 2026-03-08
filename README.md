# 4-Dimensional Political Compass

A data project mapping political ideologies, philosophies, schools of thought, and emerging movements across **four independent dimensions** of political theory. The dataset feeds a 4D scatterplot that allows visual comparison of where each entry sits relative to all others — going far beyond the traditional left/right or libertarian/authoritarian axes.

---

## Purpose

Most political compasses flatten complex traditions into one or two dimensions, forcing false proximities and obscuring genuine distinctions. This project attempts a richer mapping by scoring each entry on four orthogonal axes derived from the history of political philosophy. The goal is not to rank or judge, but to make visible the structural relationships — and surprising distances — between traditions that are often lazily grouped together.

The dataset (`political_compass.csv`) contains entries ranging from ancient philosophies to contemporary emerging movements, each scored from **-1.0 to +1.0** on all four dimensions.

---

## The Four Dimensions

### 1. Legalism ↔ Jusnaturalism
| Pole | Score | Definition |
|---|---|---|
| **Legalism** | `+1.0` | Belief that political legitimacy and rights come from statute, procedural institutions, and the "letter of the law". Laws are valid because they are enacted by the proper authority (e.g., a parliament or constitution), regardless of whether they "sound" morally perfect. Stability and order are paramount. Key concept: *Lex* (Positive Law). |
| **Jusnaturalism** | `-1.0` | Belief that legitimacy comes from inherent moral truths, human nature, or divine order, which exist *above* the state. An unjust law is no law at all. Rights (like life or liberty) are innate, not gifts from the government. Key concept: *Jus* (Right/Justice). |

---

### 2. Subsidiary ↔ Unitary
| Pole | Score | Definition |
|---|---|---|
| **Subsidiary** | `+1.0` | The principle of decentralization. Matters should be handled by the smallest, lowest, or least centralized competent authority (e.g., the individual, the family, the local community) rather than the central state. |
| **Unitary** | `-1.0` | The principle of centralization. Power should be concentrated in a single, supreme central authority to ensure efficiency, uniformity, and national cohesion. |

---

### 3. Globalism ↔ Sovereignism
| Pole | Score | Definition |
|---|---|---|
| **Globalism** | `+1.0` | Emphasis on supranational integration, open borders, and universal values. Great matters (like climate change or trade) are best solved by international cooperation and institutions (EU, UN) rather than isolated nations. |
| **Sovereignism** | `-1.0` | Emphasis on the nation-state as the supreme political unit. Priorities include national independence, border security, non-intervention, and the preservation of distinct national cultures against homogenization. |

---

### 4. Reformist ↔ Revolutionary
| Pole | Score | Definition |
|---|---|---|
| **Reformist** | `+1.0` | Change should be gradual and institutional. You work *within* the existing system (elections, laws, dialogue) to improve it without destroying the social fabric. |
| **Revolutionary** | `-1.0` | Change must be radical and immediate. The existing system is viewed as fundamentally corrupt or oppressive and must be overthrown or ruptured (violently or structurally) to build something new. |

---

## Entry Types

Each entry is classified into one of five types, which describe the nature of the political tradition rather than its content.

### 1. Ideology
A comprehensive political program or worldview that seeks to mobilize power to reshape society according to specific goals. Typically **action-oriented** (associated with a specific movement, party, or regime), **totalizing** (offering a complete package covering economics, social hierarchy, and state authority), and **historicized** (tied to a specific implementation, e.g. Stalinism, Kemalism, Nasserism).

*Examples: Marxism-Leninism, Jacobinism, Maoism, Libertarian Socialism.*

### 2. School of Thought
An intellectual tradition or academic framework that provides specific policy prescriptions and economic theories, often influencing various political actors rather than constituting a single movement. Typically **policy-focused** (concerned with mechanisms rather than total change), associated with an **academic lineage** (e.g. the Frankfurt School, Freiburg School, Austrian School), and exerts broad **influence** across multiple ideologies (e.g. Neoliberalism shaped both Thatcherism and Reaganism).

*Examples: Ordoliberalism, Fabian Socialism, Neoliberalism, Liberal Conservatism.*

### 3. Political Ethics
A normative framework focused on the moral character of governance, civic virtue, and the ethical obligations of the state and citizen. Typically **virtue-based** (emphasizing the quality and morality of the leader or citizen), **foundational** (acting as a moral precursor to fully formed ideologies), and **normative** (asking "what is the right thing to do?" rather than "how do we do it?").

*Examples: Adamsian Republicanism, Rousseauian Republicanism, Social Catholicism (Rerum Novarum), Progressive Statism.*

### 4. Philosophy
A foundational system of abstract thought that explores the underlying nature of human existence, knowledge, and social bonds — the metaphysical bedrock upon which political theories are built. Typically **pre-political** (dealing with epistemology and ontology upstream from policy), **abstract** (concerned with the human condition rather than specific laws), and **universalist** (making claims about human nature in general rather than a specific national program).

*Examples: Ubuntu Philosophy, Thomistic Natural Law, Popperian Liberalism, Comtean Positivism.*

### 5. Emerging Movement
A contemporary political paradigm or phenomenon that is currently active, evolving, and mobilizing power, but has not fully hardened into an ideology nor formalized as a political ethics. Typically **fluid and evolving** (bypassing traditional party politics through digital networks, institutional capture, or identity politics), **personality- or trend-driven** (tied to specific living personalities or rapidly mutating socio-cultural trends), and defined by **21st-century dynamics** (reacting in real-time to modern economic, technocratic, or globalist developments).

*Examples: ESG-Wokeism, Republican MAGA/Trumpism, Democrat Obama-Bidenism, Civilizational and Confucian Statisms.*

---

## Data Structure

The dataset (`political_compass.csv`) has the following columns:

| Column | Type | Description |
|---|---|---|
| `Entry` | `string` | Name of the entry |
| `Type` | `string` | One of the five entry types listed above |
| `Description` | `string` | Narrative explanation of the entry and its scores |
| `Legalism_Jusnaturalism` | `float [-1, 1]` | Score on Dimension 1 |
| `Subsidiary_Unitary` | `float [-1, 1]` | Score on Dimension 2 |
| `Globalism_Sovereignism` | `float [-1, 1]` | Score on Dimension 3 |
| `Reformist_Revolutionary` | `float [-1, 1]` | Score on Dimension 4 |

---

## Scoring Convention

Scores run from `-1.0` to `+1.0`. Verbal descriptors used in entry descriptions map approximately as follows:

| Label | Range |
|---|---|
| Maximally / Purely | ±0.85 – ±1.0 |
| Strongly | ±0.65 – ±0.84 |
| Moderately | ±0.35 – ±0.64 |
| Barely / Slightly | ±0.05 – ±0.34 |
| Neutral | ~0.0 |

---

## Visualization

The dataset is designed to feed a **4D interactive scatterplot** in which each entry appears as a point in space. Three dimensions are mapped to the X, Y, and Z axes; the fourth dimension can be represented through point color, size, or an animated slider. Points can be filtered or highlighted by entry type.
