import { isScholarshipSubcategory } from './requestAttachments'

export const SUBCATEGORY_MAP = {
  'Medical Assistance': {
    field: 'medical_assistance',
    key: 'medical',
    options: ['Medical Procedures', 'Medical Equipment', 'Medication', 'Medical Supplies', 'Natural Treatment', 'Other Medical Assistance'],
  },
  'Education Assistance': {
    field: 'educational_assistance',
    key: 'education',
    options: ['Tuition Fees', 'Transportation Fees', 'Books And Resources', 'Educational Equipment', 'Other Educational Assistance', 'Scholarship'],
  },
  'Social Assistance': {
    field: 'social_assistance',
    key: 'social',
    options: ['Garmeen', 'Orphan sponsorship', 'Marriage assistance', 'Economic empowerment assistance', 'Travel ticket assistance', 'Widow assistance', 'Divorced women assistance', 'Elderly assistance', 'Unemployed assistance', 'Visitor assistance', 'Emergency assistance', 'Psychological support assistance', 'Other social assistance'],
  },
  'Family Assistance': {
    field: 'family_assistance',
    key: 'family',
    options: ['Emergency lump-sum financial assistance', 'Monthly financial assistance', 'In-kind assistance', 'Family nursery sponsorship', 'Seasonal financial assistance', 'Food basket (food aid)', 'In-kind assistance with a monthly shopping card', 'In-kind assistance with a Ramadan shopping card', 'Utility bills', 'Fines support', 'Other family assistance'],
  },
  'Housing Assistance': {
    field: 'housing_assistance',
    key: 'housing',
    options: ['Rent support', 'Land purchase', 'Real estate purchase', 'Land purchase and construction', 'Demolition and construction', 'Maintenance and restoration', 'Furnishing support', 'Other social housing assistance'],
  },
  'Training Assistance': {
    field: 'training_assistance',
    key: 'training',
    options: ['Secretarial training', 'Entrepreneurship training', 'Student training', 'Prisoner training', 'Other training and rehabilitation'],
  },
  'Awareness Assistance': {
    field: 'awareness_assistance',
    key: 'awareness',
    options: ['National Awareness', 'Cultural Awareness', 'Social Awareness', 'Health Awareness', 'Environmental Awareness', 'Charitable Awareness', 'Consumer Awareness', 'Other Awareness Assistance'],
  },
}

export function getSubcategoryOptions(category, { includeScholarship }) {
  const options = SUBCATEGORY_MAP[category]?.options || []
  // Scholarship is applied for on /scholarship; it is listed in the form only to show an existing request.
  return options.filter(option => includeScholarship || !isScholarshipSubcategory(category, option))
}

export const SUBCATEGORY_FIELDS = Object.values(SUBCATEGORY_MAP).map(({ field }) => field)

export function getAssistanceTypeKey(row) {
  if (row.is_scholarship) return 'sidebar.scholarship'
  const { field, key } = SUBCATEGORY_MAP[row.request_category] || {}
  return field && row[field] ? `request.subtypes.${key}.${row[field]}` : ''
}
