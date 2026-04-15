
const FavorModal = {
    props: ['show', 'petList', 'currentPetIndex'],
    emits: ['close', 'select', 'reset'],
    template: `
        <transition name="modal">
            <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
                <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 m-4">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-bold text-gray-800">选择角色</h2>
                        <div class="flex items-center space-x-2">
                            <!-- 重置按钮 -->
                            <button @click="$emit('reset')" class="text-sm text-red-500 hover:text-red-700 px-2 py-1 rounded border border-red-200 hover:bg-red-50 transition-colors">
                                重置设置
                            </button>
                            <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <div class="space-y-3 max-h-96 overflow-y-auto">
                        <div v-for="pet in petList" :key="pet.index"
                             @click="$emit('select', pet.index)"
                             class="flex items-center p-3 rounded-xl cursor-pointer transition-colors border border-gray-100 hover:border-blue-300 hover:bg-blue-50"
                             :class="{'bg-blue-100 border-blue-500': currentPetIndex == pet.index}">
                            
                            <!-- 1. 头像 -->
                            <div class="w-12 h-12 rounded-full bg-gray-200 overflow-hidden mr-4 border border-gray-300 flex-shrink-0">
                                <img :src="pet.head" class="w-full h-full object-cover">
                            </div>
                            
                            <!-- 2. 文字信息 -->
                            <div class="w-24 ml-2 flex-shrink-0">
                                <div class="font-bold text-gray-800">角色 {{ pet.index }}</div>
                                <div class="text-sm text-gray-500">点击切换</div>
                            </div>

                            <!-- 3. 进度条区域 -->
                            <div class="flex-1 mx-4 flex items-center">
                                <img src="/static/assets/aixin.png" class="w-5 h-5 mr-2 flex-shrink-0">
                                <div class="w-full bg-gray-200 rounded-full h-3 border border-gray-300 relative overflow-hidden">
                                    <div class="bg-red-500 h-full rounded-full" :style="{ width: Math.min(Number(pet.favor), 100) + '%' }"></div>
                                </div>
                                <span class="ml-2 text-xs text-gray-500 w-6 text-right">{{ pet.favor }}</span>
                            </div>

                            <!-- 4. 选中图标占位符 -->
                            <div class="w-6 ml-2 flex justify-center flex-shrink-0">
                                <svg v-if="currentPetIndex == pet.index" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </transition>
    `
};

const MemoryModal = {
    props: ['show', 'modelValue'],
    emits: ['close', 'save', 'update:modelValue'],
    template: `
        <transition name="modal">
            <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
                <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 m-4 flex flex-col max-h-[80vh]">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-bold text-gray-800">记忆管理</h2>
                        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <div class="flex-1 mb-4">
                        <textarea 
                            :value="modelValue"
                            @input="$emit('update:modelValue', $event.target.value)"
                            class="w-full h-full p-4 bg-gray-50 border border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-sm leading-relaxed" 
                            placeholder="这里是 AI 的长期记忆...">
                        </textarea>
                    </div>

                    <div class="flex justify-end space-x-3">
                        <button @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">取消</button>
                        <button @click="$emit('save')" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow-md">保存记忆</button>
                    </div>
                </div>
            </div>
        </transition>
    `
};
