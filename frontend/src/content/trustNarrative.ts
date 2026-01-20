export const trustNarrative = {
  title: 'How to interpret this output',
  intro: 'SpecSharp is not here to replace judgment. It’s here to make judgment safer, faster, and more informed.',
  sections: [
    {
      id: 'assumptions',
      title: 'Key assumptions',
      bodyParagraphs: [
        'Every estimate depends on assumptions; SpecSharp surfaces key scope and cost assumptions so you can see what the number depends on.',
      ],
    },
    {
      id: 'conservative',
      title: 'Conservative bias',
      bodyParagraphs: [
        'When inputs are incomplete or ambiguous, SpecSharp defaults to conservative interpretations and flags downside risk.',
      ],
    },
    {
      id: 'uncertainty',
      title: 'Failure points',
      bodyParagraphs: [
        'Highlights sensitive drivers, high-variance items, and coordination/constructability risks.',
      ],
    },
    {
      id: 'operator',
      title: 'Operator control',
      bodyParagraphs: [
        'SpecSharp is designed to support operator adjustments and scenario testing.',
        'Today, it surfaces assumptions and risk drivers so you can sanity-check outputs quickly.',
        'Override controls are planned, not assumed.',
      ],
    },
    {
      id: 'explainable',
      title: 'Defensible logic',
      bodyParagraphs: [
        'Logic is meant to be defensible in front of principals/IC/GCs with clear rationale.',
      ],
    },
    {
      id: 'learns',
      title: 'Grounded in real data',
      bodyParagraphs: [
        'Sharing real scopes and outcomes keeps the model grounded, but any improvement depends entirely on data clarity and comparability.',
        'Treat every number as a starting point for diligence, not a promise of better outcomes.',
      ],
    },
    {
      id: 'lens',
      title: 'Decision lens',
      bodyParagraphs: [
        'Decision-support framing; reduces blind spots; trust comes from clarity, not certainty.',
      ],
    },
  ],
} as const;
