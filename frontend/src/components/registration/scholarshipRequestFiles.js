import { uploadFile } from '@/utils/fileUpload'
import { SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS } from './registrationVariant'

export function createScholarshipRequestFiles() {
  return {
    ...Object.fromEntries(SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS.map(field => [field, null])),
    other_attachments: [],
  }
}

/**
 * Upload the picked files of a scholarship request and return the request's file URLs.
 *
 * The request does not exist yet, so the files are uploaded private and unattached; the endpoint
 * attaches them after checking they are the user's own. Each URL is stored back in `files`, so a
 * retry after a failed submit reuses the uploads.
 */
export async function uploadScholarshipRequestFiles(files) {
  for (const field of SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS) {
    if (files[field] instanceof File) files[field] = await uploadPrivateFile(files[field])
  }

  const others = files.other_attachments
  for (let index = 0; index < others.length; index++) {
    if (others[index] instanceof File) others[index] = await uploadPrivateFile(others[index])
  }

  return {
    ...Object.fromEntries(SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS.map(field => [field, files[field]])),
    other_attachments: [...others],
  }
}

function uploadPrivateFile(file) {
  return uploadFile(file, { is_private: '1' })
}
