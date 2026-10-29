import { beforeEach, describe, expect, it, vi } from 'vitest'
import { uploadFile } from '@/utils/fileUpload'
import { createScholarshipRequestFiles, uploadScholarshipRequestFiles } from './scholarshipRequestFiles'

vi.mock('@/utils/fileUpload', () => ({ uploadFile: vi.fn() }))

const pdf = name => new File(['x'], name)

describe('uploadScholarshipRequestFiles', () => {
  beforeEach(() => {
    uploadFile.mockReset()
    uploadFile.mockImplementation(async file => `/private/files/${file.name}`)
  })

  it('uploads every picked file as an unattached private file', async () => {
    const files = {
      ...createScholarshipRequestFiles(),
      education_invoice: pdf('invoice.pdf'),
      grade_transcript: '/private/files/transcript.pdf',
      student_id_copy: pdf('id.pdf'),
      student_passport_copy: pdf('passport.pdf'),
      other_attachments: [pdf('extra.pdf'), '/private/files/old.pdf'],
    }

    expect(await uploadScholarshipRequestFiles(files)).toEqual({
      education_invoice: '/private/files/invoice.pdf',
      grade_transcript: '/private/files/transcript.pdf',
      student_id_copy: '/private/files/id.pdf',
      student_passport_copy: '/private/files/passport.pdf',
      other_attachments: ['/private/files/extra.pdf', '/private/files/old.pdf'],
    })
    expect(uploadFile).toHaveBeenCalledTimes(4)
    for (const [, fields] of uploadFile.mock.calls) expect(fields).toEqual({ is_private: '1' })
  })

  it('keeps the files uploaded before a failure, so a retry does not upload them again', async () => {
    const files = { ...createScholarshipRequestFiles(), education_invoice: pdf('invoice.pdf'), grade_transcript: pdf('transcript.pdf') }
    uploadFile.mockImplementationOnce(async () => '/private/files/invoice.pdf')
    uploadFile.mockImplementationOnce(async () => { throw new Error('network') })

    await expect(uploadScholarshipRequestFiles(files)).rejects.toThrow('network')
    expect(files.education_invoice).toBe('/private/files/invoice.pdf')

    await uploadScholarshipRequestFiles(files)
    expect(uploadFile.mock.calls.map(([file]) => file.name)).toEqual(['invoice.pdf', 'transcript.pdf', 'transcript.pdf'])
  })
})
