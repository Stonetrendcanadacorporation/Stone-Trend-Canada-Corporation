/**
 * Vercel serverless: quote, contact, and partner form submissions via Resend.
 *
 * Vercel environment variables:
 *   RESEND_API_KEY      from resend.com → API Keys
 *   RESEND_FROM_EMAIL   e.g. Stone Trend <noreply@yourdomain.com>
 *   FORM_EMAIL          inbox that receives submissions (default: owenkoja@stonetrend.ca)
 */
const Busboy = require('busboy');
const { sendEmail, getFormRecipient } = require('../lib/resend-mail');

module.exports.config = {
  api: {
    bodyParser: false,
  },
};

function parseMultipart(req) {
  return new Promise((resolve, reject) => {
    const fields = {};
    const files = {};

    const busboy = Busboy({ headers: req.headers });

    busboy.on('file', (name, file, info) => {
      const chunks = [];
      file.on('data', (chunk) => chunks.push(chunk));
      file.on('end', () => {
        files[name] = {
          filename: info.filename || 'attachment',
          buffer: Buffer.concat(chunks),
          mimeType: info.mimeType || 'application/octet-stream',
        };
      });
    });

    busboy.on('field', (name, value) => {
      fields[name] = value;
    });

    busboy.on('finish', () => resolve({ fields, files }));
    busboy.on('error', reject);

    req.pipe(busboy);
  });
}

function dash(value) {
  const text = (value || '').trim();
  return text || '—';
}

function buildQuoteEmail(fields) {
  const name = dash(fields.name);
  const subject = `Stone Trend – Project submission${fields.name ? ` from ${fields.name.trim()}` : ''}`;
  const text = [
    'Project submission from Stone Trend website',
    '',
    `Name: ${name}`,
    `Company: ${dash(fields.company)}`,
    `Email: ${dash(fields.email)}`,
    `Phone: ${dash(fields.phone)}`,
    `Project type: ${dash(fields['project-type'])}`,
    `Project location: ${dash(fields.location)}`,
    '',
    'Measurements & scope:',
    dash(fields.measurements),
    '',
    'Material preferences:',
    dash(fields['materials-preference']),
    '',
    '(If the visitor attached a file, it is included with this email.)',
  ].join('\n');

  return {
    subject,
    text,
    replyTo: (fields.email || '').trim() || undefined,
  };
}

function buildContactEmail(fields) {
  const name = dash(fields['contact-name']);
  const topic = dash(fields['contact-topic']);
  const subject = `Stone Trend – Contact${topic !== '—' ? ` [${topic}]` : ''}${fields['contact-name'] ? ` from ${fields['contact-name'].trim()}` : ''}`;
  const text = [
    'Contact form submission from Stone Trend website',
    '',
    `Name: ${name}`,
    `Email: ${dash(fields['contact-email'])}`,
    `Company: ${dash(fields['contact-company'])}`,
    `Topic: ${topic}`,
    '',
    'Message:',
    dash(fields['contact-message']),
  ].join('\n');

  return {
    subject,
    text,
    replyTo: (fields['contact-email'] || '').trim() || undefined,
  };
}

function buildPartnerEmail(fields) {
  const company = dash(fields['partner-company']);
  const contactName = dash(fields['partner-contact-name']);
  const subject = `Stone Trend – Partner inquiry${company !== '—' ? ` from ${company}` : contactName !== '—' ? ` from ${contactName}` : ''}`;
  const text = [
    'Partner inquiry from Stone Trend website',
    '',
    `Company: ${company}`,
    `Primary contact: ${contactName}`,
    `Email: ${dash(fields['partner-email'])}`,
    `Phone: ${dash(fields['partner-phone'])}`,
    `Trade / service category: ${dash(fields['partner-trade-type'])}`,
    `Service area: ${dash(fields['partner-service-area'])}`,
    '',
    'Website / social links:',
    dash(fields['partner-website']),
    '',
    'Notes about company:',
    dash(fields['partner-notes']),
  ].join('\n');

  return {
    subject,
    text,
    replyTo: (fields['partner-email'] || '').trim() || undefined,
  };
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  if (!process.env.RESEND_API_KEY) {
    return res.status(500).json({
      ok: false,
      error: 'Email not configured. Set RESEND_API_KEY in Vercel.',
    });
  }

  let fields;
  let files;
  try {
    ({ fields, files } = await parseMultipart(req));
  } catch (err) {
    console.error('Form parse error:', err);
    return res.status(400).json({ ok: false, error: 'Invalid form data' });
  }

  const formType = (fields.form_type || '').trim();
  let mail;
  if (formType === 'quote') {
    mail = buildQuoteEmail(fields);
  } else if (formType === 'contact') {
    mail = buildContactEmail(fields);
  } else if (formType === 'partner') {
    mail = buildPartnerEmail(fields);
  } else {
    return res.status(400).json({ ok: false, error: 'Unknown form type' });
  }

  const attachments = [];
  if (formType === 'quote' && files.attachment && files.attachment.buffer.length > 0) {
    attachments.push({
      filename: files.attachment.filename,
      content: files.attachment.buffer,
    });
  }

  try {
    await sendEmail({
      to: getFormRecipient(),
      subject: mail.subject,
      text: mail.text,
      replyTo: mail.replyTo,
      attachments,
    });

    return res.status(200).json({
      ok: true,
      message: 'Thank you. Your submission has been sent.',
    });
  } catch (err) {
    console.error('Send form error:', err);
    return res.status(500).json({
      ok: false,
      error: 'Could not send email. Please try again or email us directly.',
    });
  }
};
