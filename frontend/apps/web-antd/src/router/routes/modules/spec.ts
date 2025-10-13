import type { RouteRecordRaw } from 'vue-router';

import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'lucide:file-text',
      order: 0,
      title: '需求说明书',
    },
    name: 'Spec',
    path: '/spec',
    children: [
      {
        name: 'SpecGenerator',
        path: '/spec/generator',
        component: () => import('#/views/spec/generator/index.vue'),
        meta: {
          icon: 'lucide:file-plus',
          title: '文档生成',
        },
      },
    ],
  },
];

export default routes;
