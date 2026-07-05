export const MAX_ATTACHMENT_SIZE_MB = 15
export const MAX_ATTACHMENT_SIZE_BYTES = MAX_ATTACHMENT_SIZE_MB * 1024 * 1024

export function isFileTooLarge(file) {
  return file.size > MAX_ATTACHMENT_SIZE_BYTES
}
