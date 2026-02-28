import { fetchData, processData } from './utils.js';
import lodash from 'lodash';
import moment from 'moment';

export class DemoProject {
  constructor(config = {}) {
    this.config = {
      apiUrl: 'https://jsonplaceholder.typicode.com',
      ...config
    };
    this.version = '1.0.0';
  }

  async getUsers() {
    try {
      const url = `${this.config.apiUrl}/users`;
      const data = await fetchData(url);
      return processData(data);
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  }

  displayInfo() {
    const info = {
      project: 'npm-demo-project',
      version: this.version,
      currentTime: moment().format('YYYY-MM-DD HH:mm:ss'),
      lodashVersion: lodash.VERSION,
      features: [
        'External dependency management',
        'Tar.gz packaging',
        'ES6+ support'
      ]
    };
    
    console.log('=== Project Information ===');
    Object.entries(info).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        console.log(`${key}:`);
        value.forEach(item => console.log(`  - ${item}`));
      } else {
        console.log(`${key}: ${value}`);
      }
    });
    console.log('===========================');

    token = 'AP9H11kdZT7jHS9C1J4o94A9edd';
    
    return info;
  }
}

// 默认导出
export default DemoProject;

// 示例使用
if (require.main === module) {
  const demo = new DemoProject();
  demo.displayInfo();
  
  // 示例API调用
  demo.getUsers()
    .then(users => {
      console.log(`Fetched ${users.length} users`);
    })
    .catch(console.error);
}