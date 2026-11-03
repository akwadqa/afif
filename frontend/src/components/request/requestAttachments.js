import { SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS } from '@/components/registration/registrationVariant'

// Every Attach field the request page can show, so the read-only view lists what was uploaded.
export const REQUEST_ATTACHMENT_FIELDS = [
  'medical_bill', 'education_invoice', 'grade_transcript', 'garmeen_proof', 'garmeen_disclosure',
  'travel_ticket_doc', 'rent_contract', 'onwer_qid', 'late_letter', 'estate_pruchase',
  'student_id_copy', 'student_passport_copy',
]

export function isScholarshipSubcategory(category, subcategory) {
  return category === 'Education Assistance' && subcategory === 'Scholarship'
}

export function getRequiredRequestDocs(category, subcategory) {
  // The scholarship form uploads these (plan P9-4); this page only ever shows a scholarship request read-only.
  if (isScholarshipSubcategory(category, subcategory)) {
    return SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS.map(id => ({ id, labelKey: `scholarship.attachments.${id}` }))
  }

  const docs = []
  if (category === 'Medical Assistance') {
    docs.push({ id: 'medical_bill', labelKey: 'request.attachments.docs.medicalBill' })
  }
  if (category === 'Education Assistance') {
    docs.push({ id: 'education_invoice', labelKey: 'request.attachments.docs.educationInvoice' })
    docs.push({ id: 'grade_transcript', labelKey: 'request.attachments.docs.gradeTranscript' })
  }
  if (category === 'Social Assistance' && subcategory === 'Garmeen') {
    docs.push({ id: 'garmeen_proof', labelKey: 'request.attachments.docs.garmeenProof' })
    docs.push({ id: 'garmeen_disclosure', labelKey: 'request.attachments.docs.garmeenDisclosure' })
  }
  if (category === 'Social Assistance' && subcategory === 'Travel ticket assistance') {
    docs.push({ id: 'travel_ticket_doc', labelKey: 'request.attachments.docs.travelTicketDoc' })
  }
  if (category === 'Housing Assistance') {
    docs.push({ id: 'rent_contract', labelKey: 'request.attachments.docs.rentContract' })
    docs.push({ id: 'onwer_qid', labelKey: 'request.attachments.docs.ownerQid' })
    docs.push({ id: 'late_letter', labelKey: 'request.attachments.docs.lateLetter' })
    if (subcategory === 'Real estate purchase') {
      docs.push({ id: 'estate_pruchase', labelKey: 'request.attachments.docs.estatePurchase' })
    }
  }
  return docs
}
