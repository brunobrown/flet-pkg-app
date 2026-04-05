import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Flet PKG',
  tagline: 'Discover, explore and share Flet packages',
  favicon: 'img/logo.png',

  future: {
    v4: true,
  },

  url: 'https://brunobrown.github.io',
  baseUrl: '/flet-pkg-app/',

  organizationName: 'brunobrown',
  projectName: 'flet-pkg-app',

  onBrokenLinks: 'throw',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/brunobrown/flet-pkg-app/tree/main/docs/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/logo.png',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Flet PKG',
      logo: {
        alt: 'Flet PKG Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://flet-pkg-app.onrender.com',
          label: 'App',
          position: 'left',
        },
        {
          href: 'https://github.com/brunobrown/flet-pkg-app',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {label: 'Getting Started', to: '/docs/getting-started'},
            {label: 'Architecture', to: '/docs/architecture'},
            {label: 'Developer Guide', to: '/docs/developer-guide'},
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Flet Discord',
              href: 'https://discord.gg/dzWXP8SHG8',
            },
            {
              label: 'Flet GitHub',
              href: 'https://github.com/flet-dev/flet',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Flet PKG App',
              href: 'https://flet-pkg-app.onrender.com',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/brunobrown/flet-pkg-app',
            },
          ],
        },
      ],
      copyright: `Copyright \u00a9 ${new Date().getFullYear()} Flet PKG. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'toml', 'json'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;