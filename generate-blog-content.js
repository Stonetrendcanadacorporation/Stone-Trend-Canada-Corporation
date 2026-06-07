/**
 * Content generator for Stone Trend blog articles.
 * Produces 800-1200 word articles with intro, 4-6 sections, conclusion, and FAQ.
 * Uses safe language (no absolute claims) per legal requirements.
 */

const DISCLAIMER = 'Natural stone materials vary in colour, veining, and pattern. Material performance can vary depending on installation conditions and maintenance.';

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

function getCategory(title, index) {
  if (index < 25) return 'Countertops';
  if (index < 55) return 'Quartz Countertops';
  if (index < 85) return 'Granite Countertops';
  if (index < 110) return 'Porcelain Slabs';
  if (index < 135) return 'Quartzite Stone';
  if (index < 160) return 'Marble Countertops';
  if (index < 185) return 'Kitchen Renovation';
  if (index < 205) return 'Bathroom Renovation';
  if (index < 220) return 'Outdoor Kitchens';
  if (index < 240) return 'Home Improvement';
  if (index < 255) return 'Modern Kitchen Design';
  if (index < 270) return 'Luxury Kitchen Design';
  if (index < 285) return 'Countertop Installation';
  return 'Stone Materials';
}

const INTRO_TEMPLATES = [
  (t) => `Choosing the right surfaces for your home can feel overwhelming. Whether you're planning a kitchen renovation, updating a bathroom, or exploring options for new countertops, understanding your choices helps you make informed decisions. This guide covers ${t.toLowerCase()} to support homeowners and builders across Ontario.`,
  (t) => `Homeowners in the GTA and across Ontario often ask about ${t.toLowerCase()}. Stone Trend has supported residential and commercial projects with stone fabrication and installation for years. Here we share practical information to help you plan your next project.`,
  (t) => `When it comes to ${t.toLowerCase()}, there's a lot to consider. From material selection to installation timing, small details can affect the outcome. This article offers guidance for homeowners and builders looking for reliable information.`,
  (t) => `Whether you're in Toronto, Richmond Hill, Markham, or elsewhere in Ontario, ${t.toLowerCase()} is a common topic for anyone upgrading their space. We've compiled helpful information based on our experience in stone fabrication and installation.`,
];

const SECTION_CONTENT = {
  overview: [
    'Understanding the basics helps you communicate effectively with fabricators and designers. Many homeowners find that a bit of research before visiting showrooms leads to better outcomes. Taking time to learn about material options, typical costs, and installation processes can reduce surprises and help you ask the right questions when meeting with professionals.',
    'The first step is often understanding what options are available. Different materials offer different benefits, and what works well in one home may not suit another. Your lifestyle, cooking habits, and design preferences all play a role in selecting the right surface for your space.',
    'Material selection often depends on your lifestyle, budget, and design preferences. There is no single "best" choice—only what fits your project best. Consulting with experienced fabricators in the GTA or Ontario can help you weigh the pros and cons of each option.',
  ],
  materials: [
    'Stone materials such as quartz, granite, quartzite, marble, and porcelain each have distinct characteristics. Quartz is an engineered product known for consistency and low maintenance; natural stones like granite and quartzite offer unique veining and colour variation that many homeowners appreciate. Porcelain slabs have become increasingly popular for their versatility and performance in a range of applications.',
    'Engineered quartz is often selected for kitchens and bathrooms due to its low maintenance requirements. Natural stone can perform well when properly maintained and sealed as recommended by your fabricator. Each material has strengths that may suit different households and usage patterns.',
    'Porcelain slabs have grown in popularity for their versatility. They can be used in applications where other materials may not be suitable, including some outdoor settings. Large-format porcelain offers design flexibility and is often chosen for modern, minimalist kitchens and bathrooms.',
  ],
  cost: [
    'Costs vary based on material type, slab size, edge profile, and installation complexity. Getting quotes from local fabricators in the GTA or Ontario is the best way to understand pricing for your project. Be sure to ask what is included—some quotes cover fabrication and installation, while others may itemize these separately.',
    'Budget planning should include material, fabrication, and installation. Some homeowners are surprised by the range of options available at different price points. Mid-range materials can offer an attractive balance of aesthetics and performance without the premium cost of exotic stones.',
    'Regional pricing in Toronto, Richmond Hill, Markham, and the broader GTA can differ based on competition, supply, and overhead. It is worth contacting a few fabricators to compare options and understand what drives price differences in your area.',
  ],
  maintenance: [
    'Regular cleaning with mild soap and water is often sufficient for many stone surfaces. Avoid harsh chemicals and abrasive cleaners, as these can affect the finish over time. Wiping up spills promptly, especially acidic substances, can help maintain the appearance of your countertops.',
    'Sealing requirements depend on the material. Natural stone such as granite and marble typically benefits from periodic sealing; quartz generally does not require sealing. Your fabricator can provide specific care instructions for the material you choose.',
    'Proper care can help surfaces perform well over time. Follow the care instructions provided by your fabricator for your specific material. Using cutting boards and trivets can help protect surfaces from scratches and heat exposure.',
  ],
  installation: [
    'Professional installation is recommended for stone countertops. The process typically involves templating, fabrication, and careful installation to ensure a proper fit. Stone slabs are heavy and require experienced handlers to avoid damage during delivery and installation.',
    'Installation timelines vary. From initial measurement to final installation, many projects are completed within a few weeks, though complex projects or custom work may take longer. Discuss the timeline with your fabricator early in the process.',
    'Working with an experienced fabricator can help avoid common installation issues. Ask about their process, what to expect during the project, and how they handle cutouts for sinks and cooktops. Good communication throughout the project helps ensure a smooth experience.',
  ],
  design: [
    'Design choices such as edge profile, thickness, and colour can significantly affect the look of your space. Consider how your countertops will pair with cabinets, backsplash, and flooring. Many homeowners bring samples or photos to showroom appointments to visualize combinations.',
    'Trends in kitchen and bathroom design evolve. What matters most is choosing something that fits your style and will work for your household for years to come. Timeless options can age well, while bold choices may suit those who enjoy updating their space more frequently.',
    'Neutral tones remain popular for their versatility and ability to work with various cabinet colours and styles. Bold veining and dramatic patterns can create a statement, while subtle options offer a more understated look. Viewing full slabs in person helps you appreciate the natural variation in stone.',
  ],
  local: [
    'Stone Trend serves the GTA, including Toronto, Richmond Hill, Markham, and surrounding Ontario communities. Local fabricators can offer slab selection, custom fabrication, and professional installation. Working with a nearby fabricator can simplify communication and reduce lead times for your project.',
    'When sourcing materials in Ontario, consider working with fabricators who have established relationships with suppliers. This can affect availability and lead times. Fabricators with strong supplier networks may have access to a wider selection of slabs and colours.',
    'Homeowners in Richmond Hill, Markham, and the broader Toronto area have access to a range of stone options. Visiting showrooms and viewing slabs in person is often recommended, as photos can differ from the actual appearance of natural stone due to lighting and variation.',
  ],
};

const CONCLUSION_TEMPLATES = [
  (t) => `When it comes to ${t.toLowerCase()}, taking time to research and consult with experienced fabricators can lead to a result you are happy with. Stone Trend supports residential and commercial projects across Ontario with fabrication and installation services.`,
  (t) => `We hope this guide has provided useful information about ${t.toLowerCase()}. For personalized advice and quotes, reach out to a local fabricator. Stone Trend serves the GTA and Ontario with stone countertop fabrication and installation.`,
  (t) => `Understanding ${t.toLowerCase()} helps you make informed decisions for your home. Whether you are in Toronto, Richmond Hill, Markham, or elsewhere in Ontario, working with a qualified fabricator can make the process smoother.`,
];

function pick(arr, seed) {
  return arr[seed % arr.length];
}

function generateParagraphs(topic, category, seed, count = 2) {
  const paragraphs = [];
  const keys = Object.keys(SECTION_CONTENT);
  for (let i = 0; i < count; i++) {
    const key = keys[(seed + i) % keys.length];
    const options = SECTION_CONTENT[key];
    paragraphs.push(pick(options, seed + i * 7));
  }
  return paragraphs;
}

function generateSection(title, topic, category, seed, numSections) {
  const headings = [
    'Understanding the Basics',
    'Material Options and Benefits',
    'Cost Considerations',
    'Care and Maintenance',
    'Installation Process',
    'Design and Style Tips',
    'Local Options in Ontario',
    'What to Look For',
    'Key Considerations',
    'Practical Tips for Homeowners',
  ];
  const h2 = headings[seed % headings.length];
  const paragraphs = generateParagraphs(topic, category, seed, 3);
  return { h2, paragraphs };
}

function generateFAQ(topic, category, seed) {
  const faqPairs = [
    ['What should I consider when choosing countertop materials?', 'Consider your lifestyle, budget, design preferences, and maintenance expectations. Different materials suit different needs. Consulting with a fabricator can help narrow your options.'],
    ['How often do natural stone countertops need sealing?', 'Sealing frequency depends on the material and use. Granite and marble often benefit from sealing every 1–2 years, though this can vary. Your fabricator can provide specific recommendations.'],
    ['Is quartz better than granite?', 'Both have benefits. Quartz offers consistency and low maintenance; granite provides natural variation and is known for durability. The right choice depends on your preferences and project.'],
    ['How long does countertop installation take?', 'Many projects are completed within 2–4 weeks from measurement to installation. Complex projects or custom work may take longer. Your fabricator can provide a timeline.'],
    ['Can I use stone countertops in my bathroom?', 'Yes. Quartz, granite, quartzite, and other stone materials are commonly used for bathroom vanities. Proper sealing for natural stone can help in high-moisture areas.'],
    ['What is the cost of new countertops in Ontario?', 'Costs vary by material, size, and complexity. Getting quotes from local fabricators in the GTA or Ontario is the best way to understand pricing for your specific project.'],
    ['Does Stone Trend serve the Toronto area?', 'Yes. Stone Trend serves the GTA, including Toronto, Richmond Hill, Markham, and surrounding Ontario communities with stone fabrication and installation.'],
    ['What is the difference between quartz and quartzite?', 'Quartz is engineered stone; quartzite is natural stone. They look and perform differently. Quartzite tends to have more natural variation; quartz offers consistency.'],
    ['Are porcelain slabs suitable for kitchens?', 'Porcelain slabs can work well for kitchen countertops. They are often selected for their durability and resistance to heat and staining. Discuss your specific needs with a fabricator.'],
    ['How do I care for my stone countertops?', 'Regular cleaning with mild soap and water is typically sufficient. Avoid harsh chemicals. Natural stone may require periodic sealing. Follow care instructions from your fabricator.'],
    ['What countertop thickness should I choose?', '2cm and 3cm are common. 3cm is often used for edges that do not require a buildup; 2cm may need support for overhangs. Your fabricator can advise.'],
    ['Do countertops add resale value?', 'Quality countertops can be a selling point. Buyers often notice updated kitchens and bathrooms. The impact varies by market and the overall condition of the home.'],
  ];
  const count = 3 + (seed % 3);
  const used = new Set();
  const result = [];
  for (let i = 0; i < count && result.length < 5; i++) {
    const idx = (seed + i * 11) % faqPairs.length;
    if (used.has(idx)) continue;
    used.add(idx);
    result.push(faqPairs[idx]);
  }
  return result;
}

function generateArticle(title, index) {
  const slug = slugify(title);
  const category = getCategory(title, index);
  const seed = title.split('').reduce((a, c) => a + c.charCodeAt(0), index);

  const intro = pick(INTRO_TEMPLATES, seed)(title);
  const numSections = 4 + (seed % 3);
  const sections = [];
  for (let i = 0; i < numSections; i++) {
    sections.push(generateSection(title, title, category, seed + i * 13, numSections));
  }
  const conclusion = pick(CONCLUSION_TEMPLATES, seed + 5)(title);
  const faq = generateFAQ(title, category, seed);

  return {
    slug,
    title,
    category,
    intro,
    sections,
    conclusion,
    faq,
    disclaimer: DISCLAIMER,
  };
}

module.exports = {
  generateArticle,
  slugify,
  getCategory,
};
