<template>
  <div class="p-4">
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6" v-if="stats">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">总用户数</div>
        <div class="text-3xl font-bold text-blue-600">{{ stats.total_users }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">活跃用户</div>
        <div class="text-3xl font-bold text-green-600">{{ stats.active_users }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">管理员</div>
        <div class="text-3xl font-bold text-purple-600">{{ stats.admin_users }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">禁用用户</div>
        <div class="text-3xl font-bold text-gray-600">{{ stats.inactive_users }}</div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold">用户管理</h2>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          + 创建用户
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">姓名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap text-sm">{{ user.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">{{ user.username }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">{{ user.real_name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span v-if="user.is_admin" class="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 rounded-full">
                  管理员
                </span>
                <span v-else class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 rounded-full">
                  普通用户
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span v-if="user.is_active" class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                  正常
                </span>
                <span v-else class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-full">
                  禁用
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(user.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                <button
                  @click="openResetPasswordModal(user)"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                >
                  重置密码
                </button>
                <button
                  @click="toggleUserStatus(user)"
                  class="text-yellow-600 hover:text-yellow-800 dark:text-yellow-400"
                >
                  {{ user.is_active ? '禁用' : '启用' }}
                </button>
                <button
                  @click="deleteUser(user)"
                  class="text-red-600 hover:text-red-800 dark:text-red-400"
                  :disabled="user.is_admin && stats && stats.admin_users <= 1"
                  :class="{ 'opacity-50 cursor-not-allowed': user.is_admin && stats && stats.admin_users <= 1 }"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="users.length === 0" class="text-center py-12 text-gray-500">
          暂无用户数据
        </div>
      </div>
    </div>

    <!-- 创建用户模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showCreateModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold">创建新用户</h3>
        </div>

        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">用户名 <span class="text-red-500">*</span></label>
            <input
              v-model="createForm.username"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">姓名 <span class="text-red-500">*</span></label>
            <input
              v-model="createForm.real_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入真实姓名"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">密码 <span class="text-red-500">*</span></label>
            <input
              v-model="createForm.password"
              type="password"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="至少6位"
            />
          </div>

          <div class="flex items-center">
            <input
              v-model="createForm.is_admin"
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label class="ml-2 text-sm">设置为管理员</label>
          </div>

          <div v-if="createError" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
            {{ createError }}
          </div>
        </div>

        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-2">
          <button
            @click="showCreateModal = false; createError = ''"
            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            取消
          </button>
          <button
            @click="handleCreateUser"
            :disabled="loading"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 重置密码模态框 -->
    <div v-if="showResetPasswordModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showResetPasswordModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold">重置密码</h3>
        </div>

        <div class="px-6 py-4 space-y-4">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            为用户 <strong class="text-gray-900 dark:text-white">{{ selectedUser?.username }}</strong> 重置密码
          </p>

          <div>
            <label class="block text-sm font-medium mb-2">新密码 <span class="text-red-500">*</span></label>
            <input
              v-model="resetPasswordForm.new_password"
              type="password"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="至少6位"
            />
          </div>

          <div v-if="resetError" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
            {{ resetError }}
          </div>
        </div>

        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-2">
          <button
            @click="showResetPasswordModal = false; resetError = ''"
            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            取消
          </button>
          <button
            @click="handleResetPassword"
            :disabled="loading"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? '重置中...' : '确认重置' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { requestClient } from '#/api/request';

interface User {
  id: number;
  username: string;
  real_name: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
}

interface Stats {
  total_users: number;
  active_users: number;
  admin_users: number;
  inactive_users: number;
}

const users = ref<User[]>([]);
const stats = ref<Stats | null>(null);
const loading = ref(false);
const showCreateModal = ref(false);
const showResetPasswordModal = ref(false);
const selectedUser = ref<User | null>(null);
const createError = ref('');
const resetError = ref('');

const createForm = reactive({
  username: '',
  real_name: '',
  password: '',
  is_admin: false
});

const resetPasswordForm = reactive({
  new_password: ''
});

const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('zh-CN');
};

const loadUsers = async () => {
  try {
    loading.value = true;
    const result = await requestClient.get('/admin/users');
    users.value = result.users || [];
  } catch (error: any) {
    console.error('加载用户列表失败:', error);
    alert('加载用户列表失败: ' + (error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
};

const loadStats = async () => {
  try {
    const result = await requestClient.get('/admin/stats');
    stats.value = result;
  } catch (error: any) {
    console.error('加载统计信息失败:', error);
  }
};

const handleCreateUser = async () => {
  createError.value = '';

  if (!createForm.username || !createForm.real_name || !createForm.password) {
    createError.value = '请填写所有必填项';
    return;
  }

  if (createForm.password.length < 6) {
    createError.value = '密码长度不能少于6位';
    return;
  }

  try {
    loading.value = true;
    await requestClient.post('/admin/users', createForm);
    alert('用户创建成功！');
    showCreateModal.value = false;
    Object.assign(createForm, { username: '', real_name: '', password: '', is_admin: false });
    await loadUsers();
    await loadStats();
  } catch (error: any) {
    createError.value = error.message || '创建失败';
  } finally {
    loading.value = false;
  }
};

const openResetPasswordModal = (user: User) => {
  selectedUser.value = user;
  resetPasswordForm.new_password = '';
  resetError.value = '';
  showResetPasswordModal.value = true;
};

const handleResetPassword = async () => {
  resetError.value = '';

  if (resetPasswordForm.new_password.length < 6) {
    resetError.value = '密码长度不能少于6位';
    return;
  }

  try {
    loading.value = true;
    await requestClient.post(`/admin/users/${selectedUser.value?.id}/reset-password`, {
      new_password: resetPasswordForm.new_password
    });
    alert('密码重置成功！');
    showResetPasswordModal.value = false;
  } catch (error: any) {
    resetError.value = error.message || '重置失败';
  } finally {
    loading.value = false;
  }
};

const toggleUserStatus = async (user: User) => {
  const action = user.is_active ? '禁用' : '启用';
  if (!confirm(`确定要${action}用户 ${user.username} 吗？`)) {
    return;
  }

  try {
    loading.value = true;
    await requestClient.put(`/admin/users/${user.id}`, {
      is_active: !user.is_active
    });
    alert(`${action}成功！`);
    await loadUsers();
    await loadStats();
  } catch (error: any) {
    alert(`${action}失败: ` + (error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
};

const deleteUser = async (user: User) => {
  if (!confirm(`确定要删除用户 ${user.username} 吗？此操作不可恢复！`)) {
    return;
  }

  try {
    loading.value = true;
    await requestClient.delete(`/admin/users/${user.id}`);
    alert('删除成功！');
    await loadUsers();
    await loadStats();
  } catch (error: any) {
    alert('删除失败: ' + (error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadUsers();
  loadStats();
});
</script>
