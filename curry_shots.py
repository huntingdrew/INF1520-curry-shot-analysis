import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import players


def get_curry_shots():
    curry = [p for p in players.get_players() if p['full_name'] == 'Stephen Curry'][0]
    seasons = ['2015-16', '2016-17', '2017-18', '2018-19',
               '2019-20', '2020-21', '2021-22', '2022-23', '2023-24']
    all_shots = []
    for season in seasons:
        print(f'fetching {season}...')
        try:
            data = shotchartdetail.ShotChartDetail(
                team_id=0,
                player_id=curry['id'],
                season_nullable=season,
                season_type_all_star='Regular Season',
                context_measure_simple='FGA'
            )
            df = data.get_data_frames()[0]
            df['SEASON'] = season
            all_shots.append(df)
            time.sleep(0.6)
        except Exception as e:
            print(f'error on {season}: {e}')
    return pd.concat(all_shots, ignore_index=True)


def draw_court(ax, color='#CCCCCC', lw=1.5):
    elements = [
        Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False),
        Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color),
        Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False),
        Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color),
        Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed'),
        Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color),
        Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color),
        Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color),
        Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color),
        Circle((0, 0), radius=60, linewidth=lw, color=color, fill=False),
    ]
    for e in elements:
        ax.add_patch(e)


def plot_hexbin(df, ax, title):
    hb = ax.hexbin(
        df['LOC_X'], df['LOC_Y'],
        gridsize=25, extent=(-250, 250, -47.5, 422.5),
        cmap='YlOrRd', mincnt=1, alpha=0.85, linewidths=0.3
    )
    draw_court(ax)
    ax.set_xlim(-250, 250)
    ax.set_ylim(-50, 430)
    ax.set_facecolor('#1a1a2e')
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold', color='white', pad=10)
    return hb


def plot_zone_accuracy(df, ax):
    zone_map = {
        'Restricted Area': 'RA',
        'In The Paint (Non-RA)': 'Paint',
        'Mid-Range': 'Mid',
        'Left Corner 3': 'LC3',
        'Right Corner 3': 'RC3',
        'Above the Break 3': 'AB3',
        'Backcourt': 'BC'
    }
    stats = (df.groupby('SHOT_ZONE_BASIC')['SHOT_MADE_FLAG']
               .agg(['sum', 'count'])
               .rename(columns={'sum': 'made', 'count': 'attempts'}))
    stats['accuracy'] = stats['made'] / stats['attempts'] * 100
    stats = stats[stats['attempts'] >= 50]
    stats.index = [zone_map.get(z, z) for z in stats.index]
    stats = stats.sort_values('accuracy', ascending=True)

    colors = ['#e74c3c' if a < 40 else '#f39c12' if a < 50 else '#2ecc71'
              for a in stats['accuracy']]
    bars = ax.barh(stats.index, stats['accuracy'], color=colors, edgecolor='white', linewidth=0.5)

    for bar, (_, row) in zip(bars, stats.iterrows()):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{row['accuracy']:.1f}%  ({int(row['attempts'])}att)",
                va='center', fontsize=7.5, color='white')

    ax.set_xlabel('Field Goal %', color='white', fontsize=9)
    ax.set_title('FG% by Zone', fontsize=11, fontweight='bold', color='white')
    ax.set_facecolor('#1a1a2e')
    ax.tick_params(colors='white', labelsize=8)
    ax.set_xlim(0, 80)
    for spine in ax.spines.values():
        spine.set_edgecolor('#444')
    ax.xaxis.label.set_color('white')


def plot_3pt_trend(df, ax):
    threes = df[df['SHOT_TYPE'] == '3PT Field Goal']
    stats = (threes.groupby('SEASON')['SHOT_MADE_FLAG']
                   .agg(['sum', 'count'])
                   .rename(columns={'sum': 'made', 'count': 'att'}))
    stats['pct'] = stats['made'] / stats['att'] * 100

    x = range(len(stats))
    ax.plot(x, stats['pct'], color='#f39c12', marker='o', linewidth=2,
            markersize=7, markerfacecolor='white', markeredgecolor='#f39c12')
    ax.fill_between(x, stats['pct'], alpha=0.15, color='#f39c12')
    ax.axhline(y=stats['pct'].mean(), color='#e74c3c', linestyle='--',
               linewidth=1, alpha=0.7, label=f"Career avg: {stats['pct'].mean():.1f}%")

    ax.set_xticks(list(x))
    ax.set_xticklabels([s[:4] + '-' + s[7:] for s in stats.index], rotation=40, fontsize=7, color='white')
    ax.set_ylabel('3PT%', color='white', fontsize=9)
    ax.set_title('Career 3PT% by Season', fontsize=11, fontweight='bold', color='white')
    ax.set_facecolor('#1a1a2e')
    ax.set_ylim(30, 50)
    ax.tick_params(colors='white', labelsize=7)
    ax.yaxis.label.set_color('white')
    ax.legend(fontsize=7, labelcolor='white', facecolor='#2a2a4e', edgecolor='none')
    for spine in ax.spines.values():
        spine.set_edgecolor('#444')


def main():
    df = get_curry_shots()
    print(f'total shots: {len(df)}')

    fig = plt.figure(figsize=(16, 10), facecolor='#1a1a2e')
    fig.suptitle('Stephen Curry — Career Shot Analysis (2015–2024)',
                 fontsize=20, fontweight='bold', color='white', y=0.97)

    gs = fig.add_gridspec(2, 2, width_ratios=[1.6, 1],
                          hspace=0.45, wspace=0.3,
                          left=0.04, right=0.97, top=0.91, bottom=0.05)

    ax_main = fig.add_subplot(gs[:, 0])
    ax_zone = fig.add_subplot(gs[0, 1])
    ax_trend = fig.add_subplot(gs[1, 1])

    hb = plot_hexbin(df, ax_main,
         'Shot Frequency Map — NBA Regular Seasons 2015–16 to 2023–24\n'
         '(hex color = shots attempted; brighter = higher volume)')
    plot_zone_accuracy(df, ax_zone)
    plot_3pt_trend(df, ax_trend)

    cbar_ax = fig.add_axes([0.04, 0.02, 0.38, 0.018])
    cb = fig.colorbar(hb, cax=cbar_ax, orientation='horizontal')
    cb.set_label('Shot Attempts per Hex Cell', color='white', fontsize=8)
    cb.ax.xaxis.set_tick_params(color='white', labelcolor='white', labelsize=7)

    made = df['SHOT_MADE_FLAG'].sum()
    total = len(df)
    threes = df[df['SHOT_TYPE'] == '3PT Field Goal']
    summary = (f"Career FG: {made}/{total} ({made/total*100:.1f}%)   "
               f"3PT Attempts: {len(threes):,}   "
               f"3PT Made: {threes['SHOT_MADE_FLAG'].sum():,} ({threes['SHOT_MADE_FLAG'].mean()*100:.1f}%)")
    fig.text(0.5, 0.005, summary, ha='center', fontsize=9, color='#aaaaaa', style='italic')

    plt.savefig('curry_shot_chart.png', dpi=180, bbox_inches='tight', facecolor='#1a1a2e')
    print('saved curry_shot_chart.png')
    plt.show()


if __name__ == '__main__':
    main()
