import React from 'react';
import { Row, Col, Card, Statistic, Typography, Table, Tag, Space } from 'antd';
import { 
  UserOutlined, 
  VideoCameraOutlined, 
  ExclamationCircleOutlined,
  BellOutlined,
  EyeOutlined,
  PlayCircleOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { apiService } from '@/services/api';
import { LiveRoom, LiveStatus, UserRole } from '@/types';

const { Title } = Typography;

const Dashboard: React.FC = () => {
  // 获取统计数据
  const { data: userStats } = useQuery('user-stats', () => apiService.getUserStats());
  const { data: reportStats } = useQuery('report-stats', () => apiService.getReportStats());
  const { data: roomsData } = useQuery('rooms', () => apiService.getRooms({ limit: 10 }));
  const { data: reportsData } = useQuery('reports', () => apiService.getReports({ limit: 10 }));

  const userStatsData = userStats?.data;
  const reportStatsData = reportStats?.data;
  const rooms = roomsData?.data || [];
  const reports = reportsData?.data || [];

  // 直播状态标签
  const getStatusTag = (status: LiveStatus) => {
    const statusConfig = {
      [LiveStatus.LIVE]: { color: 'success', text: '直播中' },
      [LiveStatus.SCHEDULED]: { color: 'processing', text: '预约中' },
      [LiveStatus.ENDED]: { color: 'default', text: '已结束' },
      [LiveStatus.BANNED]: { color: 'error', text: '已封禁' },
    };
    const config = statusConfig[status];
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 举报状态标签
  const getReportStatusTag = (status: string) => {
    const statusConfig = {
      pending: { color: 'warning', text: '待处理' },
      reviewing: { color: 'processing', text: '审核中' },
      resolved: { color: 'success', text: '已解决' },
      rejected: { color: 'error', text: '已拒绝' },
    };
    const config = statusConfig[status as keyof typeof statusConfig];
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 直播房间表格列
  const roomColumns = [
    {
      title: '房间标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '主播',
      dataIndex: ['streamer', 'username'],
      key: 'streamer',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: LiveStatus) => getStatusTag(status),
    },
    {
      title: '观众数',
      dataIndex: 'viewerCount',
      key: 'viewerCount',
      render: (count: number) => (
        <Space>
          <EyeOutlined />
          {count}
        </Space>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleString(),
    },
  ];

  // 举报表格列
  const reportColumns = [
    {
      title: '举报类型',
      dataIndex: 'targetType',
      key: 'targetType',
      render: (type: string) => {
        const typeMap = {
          room: '直播房间',
          user: '用户',
          comment: '评论',
        };
        return typeMap[type as keyof typeof typeMap] || type;
      },
    },
    {
      title: '举报原因',
      dataIndex: 'reason',
      key: 'reason',
      render: (reason: string) => {
        const reasonMap = {
          spam: '垃圾信息',
          harassment: '骚扰',
          inappropriate_content: '不当内容',
          copyright_violation: '版权侵犯',
          violence: '暴力内容',
          other: '其他',
        };
        return reasonMap[reason as keyof typeof reasonMap] || reason;
      },
    },
    {
      title: '举报人',
      dataIndex: ['reporter', 'username'],
      key: 'reporter',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getReportStatusTag(status),
    },
    {
      title: '举报时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleString(),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        仪表盘
      </Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={userStatsData?.totalUsers || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃用户"
              value={userStatsData?.activeUsers || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="直播房间"
              value={rooms.length}
              prefix={<VideoCameraOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待处理举报"
              value={reportStatsData?.pendingReports || 0}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 最近直播房间 */}
        <Col xs={24} lg={12}>
          <Card title="最近直播房间" extra={<PlayCircleOutlined />}>
            <Table
              columns={roomColumns}
              dataSource={rooms}
              rowKey="_id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* 最近举报 */}
        <Col xs={24} lg={12}>
          <Card title="最近举报" extra={<ExclamationCircleOutlined />}>
            <Table
              columns={reportColumns}
              dataSource={reports}
              rowKey="_id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;