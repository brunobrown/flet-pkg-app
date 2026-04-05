import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  emoji: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Discover Packages',
    emoji: '🔍',
    description: (
      <>
        Search, filter, and sort Flet packages from the entire ecosystem.
        Data aggregated from GitHub, PyPI, and ClickHouse — all in one place.
      </>
    ),
  },
  {
    title: 'Zero-Latency Queries',
    emoji: '⚡',
    description: (
      <>
        All queries run against an in-memory index — no HTTP requests per
        interaction. Search, filter, and paginate in microseconds.
      </>
    ),
  },
  {
    title: 'Open Source',
    emoji: '🐍',
    description: (
      <>
        Built with Python and Flet 0.84+ declarative mode. Clean Architecture,
        fully tested, and open for contributions.
      </>
    ),
  },
];

function Feature({title, emoji, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <span className={styles.featureEmoji}>{emoji}</span>
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}