export const navConfig = [
  {
    key: 'aboutUs',
    route: null,
    children: [
      { key: 'aboutAfif', route: 'https://afif.qa/about/' },
      {
        key: 'governance',
        route: null,
        children: [
          { key: 'boardOfDirectors', route: 'https://afif.qa/%d9%85%d8%ac%d9%84%d8%b3-%d9%84%d8%a5%d8%af%d8%a7%d8%b1%d8%a9/' },
          { key: 'organizationalChart', route: 'https://afif.qa/organizational-chart/' },
          { key: 'financialReports', route: 'https://afif.qa/reports/' },
          { key: 'hotline', route: 'https://afif.qa/hotline/' },
        ],
      },
      { key: 'contactUs', route: 'https://afif.qa/contact/' },
    ],
  },
  {
    key: 'services',
    route: null,
    children: [
      { key: 'aiCourse', route: 'https://afif.qa/aicourse/' },
      { key: 'khaledGrant', route: 'https://afif.qa/scholarship-terms-conditions/' },
      { key: 'seasonalProjects', route: 'http://www.afif.qa/cpform' },
      { key: 'helpRequest', route: '/signin' },
    ],
  },
  {
    key: 'contactUs',
    route: 'https://afif.qa/contact/',
    children: [],
  },
]

export const donateNowRoute = 'https://donate.afif.qa/'
