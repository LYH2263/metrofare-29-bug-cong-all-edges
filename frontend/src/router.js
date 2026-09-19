import { createRouter, createWebHistory } from 'vue-router'
import LineOverview from './pages/LineOverview.vue'
import StationList from './pages/StationList.vue'
import StationDetail from './pages/StationDetail.vue'
import RoutePlanner from './pages/RoutePlanner.vue'
import FareRules from './pages/FareRules.vue'
import NetworkEdges from './pages/NetworkEdges.vue'
import TripHistory from './pages/TripHistory.vue'
import Settings from './pages/Settings.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: LineOverview },
    { path: '/stations', component: StationList },
    { path: '/stations/:code', component: StationDetail },
    { path: '/planner', component: RoutePlanner },
    { path: '/fares', component: FareRules },
    { path: '/network', component: NetworkEdges },
    { path: '/history', component: TripHistory },
    { path: '/settings', component: Settings },
  ],
})
