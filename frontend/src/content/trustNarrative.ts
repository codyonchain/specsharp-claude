export const trustNarrative = {
  title: 'How to Read Executive View',
  intro:
    'Executive View is the fast decision summary. Use it to understand the current basis, the headline recommendation, and which assumptions deserve a second look before you act.',
  sections: [
    {
      id: 'purpose',
      title: 'What this view is for',
      bodyParagraphs: [
        'Executive View is a high-level read on cost, revenue, financing, and recommendation under the current modeled basis.',
        'It is meant to tell you whether the deal looks investable enough to keep advancing, not to replace deeper underwriting or preconstruction review.',
      ],
    },
    {
      id: 'directional',
      title: 'What to treat as directional',
      bodyParagraphs: [
        'Yield, DSCR, value support, and the recommendation are only as strong as the rent, cost, scope, and financing assumptions underneath them.',
        'If one of those inputs is still moving, treat this view as a directional screen rather than a final answer.',
      ],
    },
    {
      id: 'verify',
      title: 'What to verify before acting',
      bodyParagraphs: [
        'Pressure-test the biggest assumptions first: total basis, revenue support, operating costs, lease-up or ramp timing, and debt terms.',
        'If one of those drivers is uncertain, assume the recommendation can move with it.',
      ],
    },
    {
      id: 'companions',
      title: 'How to use this with other views',
      bodyParagraphs: [
        'Use DealShield to see the first break condition and downside sensitivity. Use Construction View to inspect build-side drivers, scope burden, and schedule pressure.',
        'Read Executive View first, then use those views to validate the assumptions most likely to change the decision.',
      ],
    },
  ],
} as const;
