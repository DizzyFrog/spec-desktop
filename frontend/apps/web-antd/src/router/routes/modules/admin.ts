import type { RouteRecordRaw } from 'vue-router';

import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'lucide:shield',
      order: 999,
      title: '系统管理',
      // 只有管理员才能看到这个菜单
      authority: ['admin'],
    },
    name: 'Admin',
    path: '/admin',
    children: [
      {
        name: 'UserManagement',
        path: '/admin/users',
        component: () => import('#/views/admin/users.vue'),
        meta: {
          icon: 'lucide:users',
          title: '用户管理',
          authority: ['admin'],
        },
      },
    ],
  },
];

export default routes;
