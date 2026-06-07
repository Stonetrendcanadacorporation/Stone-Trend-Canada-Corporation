/**
 * Vercel serverless: order request emails via Resend.
 *
 * Vercel environment variables:
 *   RESEND_API_KEY
 *   RESEND_FROM_EMAIL
 *   FORM_EMAIL          Owen's inbox (default: owenkoja@stonetrend.ca)
 */
const { sendEmail, getFormRecipient } = require('../lib/resend-mail');

function buildOrderEmailHtml(data) {
  const deliveryLine = data.deliveryType === 'pickup'
    ? 'Pick up at store'
    : [data.deliveryAddress1, data.deliveryAddress2, [data.deliveryCity, data.deliveryProvince, data.deliveryPostal].filter(Boolean).join(' '), data.deliveryCountry === 'CA' ? 'Canada' : 'United States'].filter(Boolean).join(', ');
  const items = (data.cart || []).map((i) => `• ${i.title || ''} — Quantity: x${i.quantity || 1}`).join('<br>');
  return `
    <h2>Stone Trend – Order Request</h2>
    <p><strong>Reference: #${data.refNum}</strong></p>
    <hr>
    <p><strong>Customer:</strong> ${data.fullname}</p>
    ${data.company ? `<p><strong>Company:</strong> ${data.company}</p>` : ''}
    <p><strong>Email:</strong> ${data.email}</p>
    <p><strong>Phone:</strong> ${data.phone}</p>
    <p><strong>Project address/city:</strong> ${data.projectAddress}</p>
    <p><strong>Delivery:</strong> ${deliveryLine}</p>
    ${data.invoiceNumber ? `<p><strong>Invoice/PO number:</strong> ${data.invoiceNumber}</p>` : ''}
    ${data.notes ? `<p><strong>Notes:</strong> ${data.notes}</p>` : ''}
    <hr>
    <h3>Order items</h3>
    <p>${items}</p>
    <hr>
    <p>Please send a final invoice or payment link to the customer.</p>
  `.replace(/\n\s+/g, '\n').trim();
}

function buildUserConfirmationHtml(data) {
  const contactEmail = getFormRecipient();
  const items = (data.cart || []).map((i) => `• ${i.title || ''} — Quantity: x${i.quantity || 1}`).join('<br>');
  return `
    <h2>Order Request Received</h2>
    <p>Thank you, ${data.fullname}.</p>
    <p>We've received your order request and will review it shortly.</p>
    <p><strong>Reference number: #${data.refNum}</strong></p>
    <p>Please save this reference number for your records.</p>
    <hr>
    <h3>Order summary</h3>
    <p>${items}</p>
    <hr>
    <p>A final invoice or payment link will be sent to you separately.</p>
    <p>Questions? Contact us at <a href="mailto:${contactEmail}">${contactEmail}</a>.</p>
    <p>— Stone Trend Canada Corporation</p>
  `.replace(/\n\s+/g, '\n').trim();
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  if (!process.env.RESEND_API_KEY) {
    return res.status(500).json({
      error: 'Email not configured. Set RESEND_API_KEY in Vercel.',
    });
  }

  let body;
  try {
    body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
  } catch {
    return res.status(400).json({ error: 'Invalid JSON body' });
  }

  const { fullname, email, refNum, cart } = body;
  if (!fullname || !email || !refNum || !Array.isArray(cart)) {
    return res.status(400).json({ error: 'Missing required fields: fullname, email, refNum, cart' });
  }

  try {
    await sendEmail({
      to: getFormRecipient(),
      replyTo: email,
      subject: `Stone Trend – Order Request from ${fullname} [#${refNum}]`,
      html: buildOrderEmailHtml(body),
    });

    await sendEmail({
      to: email,
      subject: `Stone Trend – Order Request Received [#${refNum}]`,
      html: buildUserConfirmationHtml(body),
    });

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('Send order request error:', err);
    return res.status(500).json({ error: err.message || 'Failed to send emails' });
  }
};
