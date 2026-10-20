import { useLanguage } from '@/composables/useLanguage'

/**
 * Upload through Frappe's native /api/method/upload_file and return the file_url.
 * Pass doctype, docname and fieldname in `fields` to attach the File to a document field.
 */
export async function uploadFile(file, fields) {
  const { t } = useLanguage()
  const fd = new FormData()
  fd.append('file', file, file.name)
  fd.append('folder', 'Home/Attachments')
  for (const [key, value] of Object.entries(fields)) fd.append(key, value)

  const headers = { 'X-Frappe-Site-Name': window.location.hostname }
  if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
    headers['X-Frappe-CSRF-Token'] = window.csrf_token
  }

  const res = await fetch('/api/method/upload_file', { method: 'POST', headers, body: fd })
  if (!res.ok) {
    if (res.status === 413) throw new Error(`${t('registration.attachments.fileTooLarge')}: ${file.name}`)
    throw new Error(`${t('registration.submitError')}: ${file.name}`)
  }
  const data = await res.json()
  return data.message.file_url
}
