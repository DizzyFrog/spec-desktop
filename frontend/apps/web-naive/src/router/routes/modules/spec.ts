import type { RouteRecordRaw } from 'vue-router';

// A simple placeholder for the translation function
const $t = (key: string) => key.split('.').pop()?.replace(/_/g, ' ') || key;

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'lucide:file-text', // Using a relevant icon
      order: 10, // Position it after dashboard
      title: $t('page.spec_generator.title'),
    },
    name: 'Spec',
    path: '/spec',
    children: [
      {
        meta: {
          title: $t('page.spec_generator.generator'),
        },
        name: 'SpecGenerator',
        path: '/spec/generator',
        component: () => import('#/views/spec-generator/index.vue'),
      },
    ],
  },
];

export default routes;
